"""conquerMarket plugin tool handlers.

Read-only Conquer Online Classic market lookup via the public API.
No authentication, no state-changing requests, no browser automation.
"""

from __future__ import annotations

import json
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request

from .schemas import KNOWN_CATEGORIES, KNOWN_QUALITIES

ENDPOINT = "https://api.conqueronline.net/api/public/market/items"
TIMEOUT = 15  # seconds


def _truncate(text: str, limit: int = 2000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _validate_args(args: dict) -> dict | None:
    """Validate caller arguments. Returns an error-dict if invalid, else None."""
    error_type = None
    error_message = None

    # ---- page ----
    page = args.get("page", 1)
    if not isinstance(page, int) or isinstance(page, bool):
        error_type = "invalid_argument"
        error_message = "'page' must be an integer >= 1"
    elif page < 1:
        error_type = "invalid_argument"
        error_message = "'page' must be >= 1"

    # ---- page_size ----
    page_size = args.get("page_size", 50)
    if not isinstance(page_size, int) or isinstance(page_size, bool):
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'page_size' must be an integer"
    elif page_size < 1:
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'page_size' must be >= 1"
    elif page_size > 50:
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'page_size' must be <= 50"

    # ---- plus ----
    plus = args.get("plus", None)
    if plus is not None:
        if not isinstance(plus, int) or isinstance(plus, bool):
            error_type = error_type or "invalid_argument"
            error_message = error_message or "'plus' must be an integer"
        elif plus < 0:
            error_type = error_type or "invalid_argument"
            error_message = error_message or "'plus' must be a non-negative integer"

    # ---- category ----
    category = args.get("category", None)
    if category is not None and category not in KNOWN_CATEGORIES:
        error_type = error_type or "invalid_argument"
        error_message = error_message or (
            f"Unknown category '{category}'. Known: {', '.join(sorted(KNOWN_CATEGORIES))}"
        )

    # ---- quality ----
    quality = args.get("quality", None)
    if quality is not None and quality not in KNOWN_QUALITIES:
        error_type = error_type or "invalid_argument"
        error_message = error_message or (
            f"Unknown quality '{quality}'. Known: {', '.join(sorted(KNOWN_QUALITIES))}"
        )

    # ---- sort / direction ----
    sort = args.get("sort", 4)
    if not isinstance(sort, int) or isinstance(sort, bool):
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'sort' must be an integer"

    direction = args.get("direction", 0)
    if not isinstance(direction, int) or isinstance(direction, bool):
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'direction' must be an integer"

    # ---- server ----
    server = args.get("server", 0)
    if not isinstance(server, int) or isinstance(server, bool):
        error_type = error_type or "invalid_argument"
        error_message = error_message or "'server' must be an integer"

    if error_type:
        return {
            "ok": False,
            "endpoint": ENDPOINT,
            "params": {},
            "http_status": None,
            "error": {"type": error_type, "message": error_message},
        }
    return None


def _build_params(args: dict) -> dict:
    """Build API query params from validated args, omitting nulls."""
    params = {
        "server": int(args.get("server", 0)),
        "sort": int(args.get("sort", 4)),
        "direction": int(args.get("direction", 0)),
        "page": int(args.get("page", 1)),
        "pageSize": int(args.get("page_size", 50)),
    }
    category = args.get("category")
    if category is not None:
        params["category"] = category
    subcategory = args.get("subcategory")
    if subcategory is not None:
        params["subcategory"] = subcategory
    quality = args.get("quality")
    if quality is not None:
        params["quality"] = quality
    plus = args.get("plus")
    if plus is not None:
        params["plus"] = int(plus)
    return params


def _do_request(params: dict) -> dict:
    """Perform the HTTPS GET with a single retry for transient network errors."""
    query_string = urllib.parse.urlencode(params, doseq=False)
    url = f"{ENDPOINT}?{query_string}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    last_exc = None
    for attempt in range(2):  # initial + 1 retry
        try:
            req = urllib.request.Request(url, headers=headers, method="GET")
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                status = resp.getcode()
                body = resp.read()
            if not (200 <= status < 300):
                return {
                    "ok": False,
                    "endpoint": ENDPOINT,
                    "params": params,
                    "http_status": status,
                    "error": {
                        "type": "http_error",
                        "message": f"API returned HTTP {status}",
                        "body_preview": _truncate(body.decode("utf-8", errors="replace")),
                    },
                }
            try:
                data = json.loads(body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                preview = _truncate(body.decode("utf-8", errors="replace"))
                return {
                    "ok": False,
                    "endpoint": ENDPOINT,
                    "params": params,
                    "http_status": status,
                    "error": {
                        "type": "invalid_json_response",
                        "message": "Response body was not valid JSON",
                        "body_preview": preview,
                    },
                }
            return {
                "ok": True,
                "endpoint": ENDPOINT,
                "params": params,
                "http_status": status,
                "data": data,
            }
        except urllib.error.HTTPError as exc:
            # 4xx — do not retry
            if 400 <= exc.code < 500:
                body_text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
                return {
                    "ok": False,
                    "endpoint": ENDPOINT,
                    "params": params,
                    "http_status": exc.code,
                    "error": {
                        "type": "http_error",
                        "message": f"API returned HTTP {exc.code}",
                        "body_preview": _truncate(body_text),
                    },
                }
            # 5xx or other — retry once
            last_exc = exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_exc = exc
        # brief delay before retry
        import time
        time.sleep(0.5)

    # All retries exhausted
    exc = last_exc
    return {
        "ok": False,
        "endpoint": ENDPOINT,
        "params": params,
        "http_status": None,
        "error": {
            "type": "network_error",
            "message": f"Request failed after retry: {type(exc).__name__}: {exc}",
        },
    }


def conquer_market_search(args: dict, **kwargs) -> str:
    """Search the public Conquer Online Classic market API.

    Args: passed by Hermes as a dict of the tool's input parameters.

    Returns a JSON string with the result envelope.
    """
    # Validate first
    validation_error = _validate_args(args)
    if validation_error:
        return json.dumps(validation_error, indent=2)

    params = _build_params(args)
    result = _do_request(params)
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Local client-data catalog lookup (conquer_game_data_search)
# ---------------------------------------------------------------------------

from . import importer as _importer  # delayed import to avoid cycle issues

_VALID_RESOURCES = {"item", "monster", "magic"}

_RESOURCE_TABLE = {
    "item": "item",
    "monster": "monster",
    "magic": "magic",
}

# Columns surfaced in search results (sanitized, no secrets/paths/sql).
_RESOURCE_COLUMNS = {
    "item": [
        "id", "name", "description", "price", "weight", "required_level",
        "required_profession", "required_weapon_skill", "attack_min",
        "attack_max", "attack_speed", "attack_range", "defense", "dexterity",
        "dodge", "life", "mana", "magic_attack", "magic_defense",
        "gem1", "gem2", "magic1", "magic2", "magic3", "monopoly", "ident",
    ],
    "monster": [
        "type", "name", "level", "max_life", "body_type", "size_add",
        "zoom_percent", "born_action", "act_res_ctrl", "asb", "adb",
    ],
    "magic": [
        "magic_type", "level", "name", "disc", "power", "mp_cost",
        "use_pp", "duration", "range", "exp_required", "learn_level",
        "professional_req", "weapon_subtype", "action_sort", "multi",
    ],
}

# Human-facing label for each resource's name/display field.
_NAME_FIELD = {"item": "name", "monster": "name", "magic": "name"}


def _catalog_meta() -> dict:
    """Build the metadata envelope shared across all responses.

    Never raises: if the DB or manifest is missing, degrades gracefully.
    """
    meta = {
        "source_type": "local_client_catalog",
        "catalog_version": None,
        "source_version": None,
        "importer_version": None,
        "imported_at_utc": None,
        "record_counts": {"item": None, "monster": None, "magic": None},
        "sources": {},
        "present": False,
    }
    try:
        man = _importer.latest_manifest()
        if man:
            meta["present"] = True
            meta["catalog_version"] = man.get("catalog_version")
            meta["importer_version"] = man.get("importer_version")
            meta["imported_at_utc"] = man.get("imported_at_utc")
            meta["record_counts"] = {
                "item": man.get("itemtype_records"),
                "monster": man.get("monster_records"),
                "magic": man.get("magictype_records"),
            }
            meta["sources"] = {
                "item": {
                    "sha256": man.get("itemtype_sha256"),
                    "size": man.get("itemtype_bytes"),
                    "records": man.get("itemtype_records"),
                },
                "monster": {
                    "sha256": man.get("monster_sha256"),
                    "size": man.get("monster_bytes"),
                    "records": man.get("monster_records"),
                },
                "magic": {
                    "sha256": man.get("magictype_sha256"),
                    "size": man.get("magictype_bytes"),
                    "records": man.get("magictype_records"),
                },
            }
    except Exception:
        # Degrade: metadata still returned, just without catalog details.
        pass
    return meta


def _error_response(error_type: str, message: str, meta: dict, **extra) -> str:
    payload = {
        "ok": False,
        "source_type": "local_client_catalog",
        "catalog_version": meta.get("catalog_version"),
        "catalog_metadata": meta,
        "error": {"type": error_type, "message": message},
    }
    payload.update(extra)
    return json.dumps(payload, indent=2)


def _row_to_dict(row, columns):
    return {c: row[idx] for idx, c in enumerate(columns)}


def conquer_game_data_search(args: dict, **kwargs) -> str:
    """Read-only lookup against the local client-data catalog (SQLite).

    Args: passed by Hermes as a dict with 'resource', 'query', 'id', 'limit'.

    Returns a JSON string. Every code path returns valid JSON and never raises
    into the Hermes tool loop.
    """
    meta = _catalog_meta()

    # ---- validation -------------------------------------------------------
    resource = args.get("resource")
    if resource not in _VALID_RESOURCES:
        return _error_response(
            "validation_error",
            f"Invalid resource '{resource}'. Must be one of: item, monster, magic.",
            meta,
            resource=resource,
        )

    query = args.get("query")
    qid = args.get("id")
    limit = args.get("limit", 20)

    if not (query or qid is not None):
        return _error_response(
            "validation_error",
            "A query or id is required.",
            meta,
            resource=resource,
            query=query,
            id=qid,
            limit=limit,
        )

    # Coerce + clamp limit (1..50)
    if limit is None:
        limit = 20
    try:
        limit = int(limit)
        if isinstance(args.get("limit"), bool):
            raise ValueError
    except (TypeError, ValueError):
        return _error_response(
            "validation_error",
            "'limit' must be an integer between 1 and 50.",
            meta,
            resource=resource,
            query=query,
            id=qid,
            limit=limit,
        )
    if limit < 1:
        limit = 1
    if limit > 50:
        return _error_response(
            "validation_error",
            "'limit' cannot exceed 50.",
            meta,
            resource=resource,
            query=query,
            id=qid,
            limit=limit,
        )

    # ---- query the catalog (parameterized) --------------------------------
    db_path = _importer.db_path()
    if not db_path.exists():
        return _error_response(
            "catalog_unavailable",
            "The local client-data catalog has not been built yet. "
            "Run the importer before searching.",
            meta,
            resource=resource,
            query=query,
            id=qid,
            limit=limit,
        )

    table = _RESOURCE_TABLE[resource]
    name_field = _NAME_FIELD[resource]
    columns = _RESOURCE_COLUMNS[resource]
    col_list = ", ".join(columns)
    id_field = "id" if resource == "item" else ("type" if resource == "monster" else "magic_type")
    level_field = "level" if resource == "magic" else None

    results = []
    count = 0
    try:
        # Open read-only: the catalog is immutable at query time, so a buggy
        # handler can never mutate it. uri=True enables the file: query string.
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        if qid is not None:
            # Exact ID lookup.
            try:
                qid_int = int(qid)
            except (TypeError, ValueError):
                return _error_response(
                    "validation_error",
                    "'id' must be an integer.",
                    meta,
                    resource=resource,
                    query=query,
                    id=qid,
                    limit=limit,
                )
            if resource == "magic":
                # magic has composite key (magic_type, level); match all levels.
                rows = conn.execute(
                    f"SELECT {col_list} FROM {table} WHERE {id_field} = ? ORDER BY level LIMIT ?",
                    (qid_int, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    f"SELECT {col_list} FROM {table} WHERE {id_field} = ? LIMIT ?",
                    (qid_int, limit),
                ).fetchall()
            results = [_row_to_dict(r, columns) for r in rows]
            count = len(results)
        else:
            # Substring text search on the name field, case-insensitive.
            # SQLite LIKE with ESCAPE; we bound by limit.
            like = f"%{query}%"
            rows = conn.execute(
                f"SELECT {col_list} FROM {table} WHERE {name_field} LIKE ? ESCAPE '\\' "
                f"ORDER BY {name_field} LIMIT ?",
                (like, limit),
            ).fetchall()
            results = [_row_to_dict(r, columns) for r in rows]
            count = len(results)
        conn.close()
    except sqlite3.Error as exc:
        return _error_response(
            "catalog_error",
            f"Database error: {exc}",
            meta,
            resource=resource,
            query=query,
            id=qid,
            limit=limit,
        )

    return json.dumps(
        {
            "ok": True,
            "source_type": "local_client_catalog",
            "catalog_version": meta.get("catalog_version"),
            "catalog_metadata": meta,
            "resource": resource,
            "query": query,
            "id": qid,
            "count": count,
            "limit": limit,
            "results": results,
        },
        indent=2,
        ensure_ascii=False,
    )
