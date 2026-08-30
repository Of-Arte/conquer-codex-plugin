"""conquer-market plugin tool handlers.

Read-only Conquer Online Classic market lookup via the public API.
No authentication, no state-changing requests, no browser automation.
"""

from __future__ import annotations

import json
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
