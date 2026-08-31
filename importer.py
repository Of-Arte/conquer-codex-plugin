"""Local client-data catalog importer for the conquerMarket plugin.

Reads the three raw reference JSON files (itemtype.json, monster.json,
magictype.json) from the plugin's ``plugin-data/conquerMarket/source/``
directory and materializes them into a read-only SQLite database under
``plugin-data/conquerMarket/catalog/``.

Design goals
------------
* Standard library only (json, hashlib, sqlite3, pathlib, datetime).
* Idempotent and safe to rerun.
* Records source hashes, file sizes, record counts, importer version and
  import time in a ``manifest`` table.
* Refuses to build a catalog when the source hashes changed since the last
  successful import (stale catalog detection). Re-running with new sources
  rebuilds the database atomically.
* Reports invalid records without aborting the whole import.
* NEVER modifies the raw source files.

Paths are resolved relative to the plugin package directory so the behavior
is identical regardless of the active Hermes profile home.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Importer identity ----------------------------------------------------------
IMPORTER_VERSION = "conquerMarket-importer-v1"

# Resolved relative to this file: plugins/conquerMarket/importer.py
# parent = plugins/conquerMarket
# parent.parent = profiles/conquer
# / plugin-data / conquerMarket
_THIS_FILE = Path(__file__).resolve()
_PLUGIN_ROOT = _THIS_FILE.parent                      # .../plugins/conquerMarket
_PROFILE_ROOT = _PLUGIN_ROOT.parent.parent           # .../profiles/conquer
_DATA_ROOT = _PROFILE_ROOT / "plugin-data" / "conquerMarket"

SOURCE_DIR = _DATA_ROOT / "source"
CATALOG_DIR = _DATA_ROOT / "catalog"
MANIFEST_DIR = _DATA_ROOT / "manifests"

DB_PATH = CATALOG_DIR / "conquer_client_catalog.sqlite3"
MANIFEST_PATH = MANIFEST_DIR / "import-manifest.json"

SOURCE_FILES = {
    "item": "itemtype.json",
    "monster": "monster.json",
    "magic": "magictype.json",
}


# ---------------------------------------------------------------------------
# Hash + size helpers
# ---------------------------------------------------------------------------

def _sha256_and_size(path: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def source_fingerprints() -> dict:
    """Return {resource: {path, sha256, size, exists}} for each source file."""
    fp = {}
    for resource, fname in SOURCE_FILES.items():
        p = SOURCE_DIR / fname
        entry = {
            "path": str(p),
            "sha256": None,
            "size": None,
            "exists": p.exists(),
        }
        if p.exists() and p.is_file():
            entry["sha256"], entry["size"] = _sha256_and_size(p)
        fp[resource] = entry
    return fp


# ---------------------------------------------------------------------------
# Manifest read/write
# ---------------------------------------------------------------------------

def read_manifest() -> dict | None:
    if not MANIFEST_PATH.exists():
        return None
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


def write_manifest(manifest: dict) -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    tmp = MANIFEST_PATH.with_name(MANIFEST_PATH.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    tmp.replace(MANIFEST_PATH)


# ---------------------------------------------------------------------------
# Catalog version (deterministic from source hashes)
# ---------------------------------------------------------------------------

def catalog_version_from_fingerprints(fp: dict) -> str:
    parts = []
    for r in ("item", "monster", "magic"):
        h = fp.get(r, {}).get("sha256") or ""
        parts.append(h)
    return "|".join(parts)


# ---------------------------------------------------------------------------
# SQLite schema
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS manifest (
    catalog_version  TEXT PRIMARY KEY,
    importer_version TEXT,
    imported_at_utc  TEXT,
    itemtype_sha256  TEXT,
    itemtype_bytes   INTEGER,
    itemtype_records INTEGER,
    monster_sha256   TEXT,
    monster_bytes    INTEGER,
    monster_records  INTEGER,
    magictype_sha256 TEXT,
    magictype_bytes  INTEGER,
    magictype_records INTEGER
);

CREATE TABLE IF NOT EXISTS item (
    id                   INTEGER PRIMARY KEY,
    name                 TEXT,
    description          TEXT,
    price                INTEGER,
    weight               INTEGER,
    amount               INTEGER,
    amount_limit         INTEGER,
    required_level       INTEGER,
    required_profession  INTEGER,
    required_sex         INTEGER,
    required_strength    INTEGER,
    required_agility     INTEGER,
    required_vitality    INTEGER,
    required_spirit      INTEGER,
    required_weapon_skill INTEGER,
    attack_min           INTEGER,
    attack_max           INTEGER,
    attack_speed         INTEGER,
    attack_range         INTEGER,
    defense              INTEGER,
    dexterity            INTEGER,
    dodge                INTEGER,
    life                 INTEGER,
    mana                 INTEGER,
    magic_attack         INTEGER,
    magic_defense        INTEGER,
    gem1                 INTEGER,
    gem2                 INTEGER,
    magic1               INTEGER,
    magic2               INTEGER,
    magic3               INTEGER,
    monopoly             INTEGER,
    ident                INTEGER
);

CREATE TABLE IF NOT EXISTS monster (
    type          INTEGER PRIMARY KEY,
    name          TEXT,
    level         INTEGER,
    max_life      INTEGER,
    size_add      INTEGER,
    zoom_percent  INTEGER,
    born_action   INTEGER,
    body_type     INTEGER,
    born_effect   TEXT,
    born_sound    TEXT,
    act_res_ctrl  INTEGER,
    asb           INTEGER,
    adb           INTEGER
);

CREATE TABLE IF NOT EXISTS magic (
    magic_type          INTEGER,
    level               INTEGER,
    name                TEXT,
    disc                TEXT,
    disc_ex             TEXT,
    exp_required        INTEGER,
    learn_level         INTEGER,
    monster_level_req   INTEGER,
    power               INTEGER,
    range               INTEGER,
    mp_cost             INTEGER,
    use_pp              INTEGER,
    duration            INTEGER,
    active_time         INTEGER,
    intone_duration     INTEGER,
    target_delay        INTEGER,
    target_wound_delay  INTEGER,
    hitpoint            INTEGER,
    distance            INTEGER,
    next_magic          INTEGER,
    professional_req    INTEGER,
    weapon_subtype      INTEGER,
    action_sort         INTEGER,
    status              INTEGER,
    auto_active         INTEGER,
    auto_learn          INTEGER,
    magic_break         INTEGER,
    drop_weapon         INTEGER,
    ground              INTEGER,
    floor_attribute     INTEGER,
    client_represent      INTEGER,
    screen_represent    INTEGER,
    can_be_used_in_market INTEGER,
    crime               INTEGER,
    multi               INTEGER,
    xp                  INTEGER,
    ground_effect       TEXT,
    intone_effect       TEXT,
    intone_sound        TEXT,
    sender_action       INTEGER,
    sender_effect       TEXT,
    sender_sound        TEXT,
    target_effect       TEXT,
    target_sound        TEXT,
    trace_effect        TEXT,
    PRIMARY KEY (magic_type, level)
);

CREATE INDEX IF NOT EXISTS idx_item_name        ON item(name);
CREATE INDEX IF NOT EXISTS idx_item_req_level   ON item(required_level);
CREATE INDEX IF NOT EXISTS idx_item_profession  ON item(required_profession);
CREATE INDEX IF NOT EXISTS idx_monster_name     ON monster(name);
CREATE INDEX IF NOT EXISTS idx_monster_level    ON monster(level);
CREATE INDEX IF NOT EXISTS idx_magic_name       ON magic(name);
CREATE INDEX IF NOT EXISTS idx_magic_type       ON magic(magic_type);
"""


# ---------------------------------------------------------------------------
# Loaders (each yields (record, error_or_None) — never raises on bad record)
# ---------------------------------------------------------------------------

_ITEM_KEYS = [
    "id", "name", "description", "price", "weight", "amount", "amountLimit",
    "requiredLevel", "requiredProfession", "requiredSex", "requiredStrength",
    "requiredAgility", "requiredVitality", "requiredSpirit",
    "requiredWeaponSkill", "attackMin", "attackMax", "attackSpeed",
    "attackRange", "defense", "dexterity", "dodge", "life", "mana",
    "magicAttack", "magicDefense", "gem1", "gem2", "magic1", "magic2", "magic3",
    "monopoly", "ident",
]


def _load_records(path: Path) -> list:
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        raw = json.load(fh)
    if not isinstance(raw, list):
        raise ValueError(f"{path.name}: expected top-level JSON array, got {type(raw).__name__}")
    return raw


def _insert_items(conn: sqlite3.Connection, records: list) -> tuple[int, int, list]:
    inserted = 0
    skipped = 0
    errors = []
    cur = conn.cursor()
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            skipped += 1
            errors.append({"record_index": i, "reason": f"not an object: {type(rec).__name__}"})
            continue
        vals = []
        for k in _ITEM_KEYS:
            v = rec.get(k)
            vals.append(v)
        # amountLimit maps to amount_limit, rename handled below via positional
        try:
            cur.execute(
                "INSERT OR REPLACE INTO item ("
                "id,name,description,price,weight,amount,amount_limit,"
                "required_level,required_profession,required_sex,"
                "required_strength,required_agility,required_vitality,"
                "required_spirit,required_weapon_skill,attack_min,attack_max,"
                "attack_speed,attack_range,defense,dexterity,dodge,life,mana,"
                "magic_attack,magic_defense,gem1,gem2,magic1,magic2,magic3,"
                "monopoly,ident) "
                "VALUES (" + ",".join(["?"] * len(_ITEM_KEYS)) + ")",
                vals,
            )
            inserted += 1
        except sqlite3.Error as exc:
            skipped += 1
            rid = rec.get("id", f"index:{i}")
            errors.append({"record_index": i, "id": rid, "reason": str(exc)})
    conn.commit()
    return inserted, skipped, errors


_MONSTER_KEYS = [
    "type", "name", "level", "maxLife", "sizeAdd", "zoomPercent", "bornAction",
    "bodyType", "bornEffect", "bornSound", "actResCtrl", "asb", "adb",
]


def _insert_monsters(conn, records):
    inserted = 0
    skipped = 0
    errors = []
    cur = conn.cursor()
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            skipped += 1
            errors.append({"record_index": i, "reason": f"not an object: {type(rec).__name__}"})
            continue
        vals = [rec.get(k) for k in _MONSTER_KEYS]
        try:
            cur.execute(
                "INSERT OR REPLACE INTO monster ("
                "type,name,level,max_life,size_add,zoom_percent,born_action,"
                "body_type,born_effect,born_sound,act_res_ctrl,asb,adb) "
                "VALUES (" + ",".join(["?"] * len(_MONSTER_KEYS)) + ")",
                vals,
            )
            inserted += 1
        except sqlite3.Error as exc:
            skipped += 1
            mtid = rec.get("type", f"index:{i}")
            errors.append({"record_index": i, "type": mtid, "reason": str(exc)})
    conn.commit()
    return inserted, skipped, errors


# (magic_type, level) is the composite primary key
_MAGIC_KEYS = [
    "MagicType", "Level", "Name", "Disc", "DiscEx", "ExpRequired", "LearnLevel",
    "MonsterLevelRequired", "Power", "Range", "MpCost", "UsePP", "Duration",
    "ActiveTime", "IntoneDuration", "TargetDelay", "TargetWoundDelay",
    "HitPoint", "Distance", "NextMagic", "ProfessionalRequired", "WeaponSubType",
    "ActionSort", "Status", "AutoActive", "AutoLearn", "MagicBreak", "DropWeapon",
    "Ground", "FloorAttribute", "ClientRepresent", "ScreenRepresent",
    "CanBeusedInMarket", "Crime", "Multi", "Xp", "GroundEffect",
    "IntoneEffect", "IntoneSound", "SenderAction", "SenderEffect",
    "SenderSound", "TargetEffect", "TargetSound", "TraceEffect",
]


def _insert_magic(conn, records):
    inserted = 0
    skipped = 0
    errors = []
    cur = conn.cursor()
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            skipped += 1
            errors.append({"record_index": i, "reason": f"not an object: {type(rec).__name__}"})
            continue
        vals = [rec.get(k) for k in _MAGIC_KEYS]
        try:
            cur.execute(
                "INSERT OR REPLACE INTO magic ("
                "magic_type,level,name,disc,disc_ex,exp_required,learn_level,"
                "monster_level_req,power,range,mp_cost,use_pp,duration,"
                "active_time,intone_duration,target_delay,target_wound_delay,"
                "hitpoint,distance,next_magic,professional_req,weapon_subtype,"
                "action_sort,status,auto_active,auto_learn,magic_break,drop_weapon,"
                "ground,floor_attribute,client_represent,screen_represent,"
                "can_be_used_in_market,crime,multi,xp,ground_effect,intone_effect,"
                "intone_sound,sender_action,sender_effect,sender_sound,target_effect,"
                "target_sound,trace_effect) "
                "VALUES (" + ",".join(["?"] * len(_MAGIC_KEYS)) + ")",
                vals,
            )
            inserted += 1
        except sqlite3.Error as exc:
            skipped += 1
            mid = rec.get("MagicType", f"index:{i}")
            errors.append({"record_index": i, "MagicType": mid, "Level": rec.get("Level"), "reason": str(exc)})
    conn.commit()
    return inserted, skipped, errors


# ---------------------------------------------------------------------------
# Main import entry point
# ---------------------------------------------------------------------------

def import_catalog(force: bool = False) -> dict:
    """Build or rebuild the local SQLite catalog from the raw JSON sources.

    Returns a dict describing what happened. The catalog_version is derived
    from the concatenated SHA-256 of the three source files, so any change to
    the raw data automatically invalidates the on-disk catalog.

    Parameters
    ----------
    force : bool
        If True, rebuild even when fingerprints match.
    """
    fp = source_fingerprints()

    # Verify all sources exist
    missing = [r for r, e in fp.items() if not e["exists"]]
    if missing:
        return {
            "ok": False,
            "error": {
                "type": "missing_source",
                "message": f"Missing source files: {missing}",
                "paths": {r: fp[r]["path"] for r in missing},
            },
        }

    catalog_version = catalog_version_from_fingerprints(fp)
    prev_manifest = read_manifest()

    # Stale catalog detection: refuse to silently use changed sources.
    if not force and prev_manifest is not None:
        prev_ver = prev_manifest.get("catalog_version")
        if prev_ver is None:
            # Manifest missing version field — treat as stale to be safe.
            pass
        elif prev_ver != catalog_version:
            return {
                "ok": False,
                "error": {
                    "type": "stale_source",
                    "message": (
                        "Source files have changed since the last import. "
                        "The local catalog would be stale. Re-run with "
                        "force=True to rebuild."
                    ),
                    "old_version": prev_ver,
                    "new_version": catalog_version,
                    "prev_imported_at": prev_manifest.get("imported_at_utc"),
                },
            }
        else:
            # Already up to date — verify DB exists and is intact.
            if DB_PATH.exists() and _db_verified(catalog_version):
                man = read_manifest()
                rc = {
                    "item": man.get("itemtype_records") if man else None,
                    "monster": man.get("monster_records") if man else None,
                    "magic": man.get("magictype_records") if man else None,
                } if man else None
                return {
                    "ok": True,
                    "rebuilt": False,
                    "catalog_version": catalog_version,
                    "db_path": str(DB_PATH),
                    "record_counts": rc,
                    "skipped_import": "catalog already current",
                }
            # DB missing/corrupt but hashes match — rebuild.

    # ---- Build phase: write to a temp DB then atomically replace ----
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    tmp_db = DB_PATH.with_name(DB_PATH.name + ".tmp")
    if tmp_db.exists():
        tmp_db.unlink()

    loaded = {}
    counts = {}
    import_errors = {}
    for resource in ("item", "monster", "magic"):
        fname = SOURCE_FILES[resource]
        path = SOURCE_DIR / fname
        try:
            loaded[resource] = _load_records(path)
            counts[resource] = len(loaded[resource])
        except (json.JSONDecodeError, ValueError, OSError) as exc:
            loaded[resource] = []
            counts[resource] = 0
            import_errors[resource] = {
                "reason": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(),
            }

    conn = sqlite3.connect(str(tmp_db))
    conn.executescript(SCHEMA_SQL)

    inserted = {}
    skipped = {}
    errors = {}

    if loaded["item"]:
        inserted["item"], skipped["item"], errors["item"] = _insert_items(conn, loaded["item"])
    else:
        inserted["item"] = skipped["item"] = 0
    if loaded["monster"]:
        inserted["monster"], skipped["monster"], errors["monster"] = _insert_monsters(conn, loaded["monster"])
    else:
        inserted["monster"] = skipped["monster"] = 0
    if loaded["magic"]:
        inserted["magic"], skipped["magic"], errors["magic"] = _insert_magic(conn, loaded["magic"])
    else:
        inserted["magic"] = skipped["magic"] = 0

    now_utc = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO manifest "
        "(catalog_version, importer_version, imported_at_utc, "
        "itemtype_sha256, itemtype_bytes, itemtype_records, "
        "monster_sha256, monster_bytes, monster_records, "
        "magictype_sha256, magictype_bytes, magictype_records) "
        "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            catalog_version, IMPORTER_VERSION, now_utc,
            fp["item"]["sha256"], fp["item"]["size"], counts["item"],
            fp["monster"]["sha256"], fp["monster"]["size"], counts["monster"],
            fp["magic"]["sha256"], fp["magic"]["size"], counts["magic"],
        ),
    )
    conn.commit()
    conn.close()

    # Atomic move into place (build a fresh, complete DB first).
    if DB_PATH.exists():
        DB_PATH.unlink()
    tmp_db.replace(DB_PATH)

    # Write the external manifest JSON (mirrors the SQL manifest table)
    manifest_doc = {
        "catalog_version": catalog_version,
        "importer_version": IMPORTER_VERSION,
        "imported_at_utc": now_utc,
        "db_path": str(DB_PATH),
        "itemtype_records": counts["item"],
        "monster_records": counts["monster"],
        "magictype_records": counts["magic"],
        "sources": {
            r: {
                "path": fp[r]["path"],
                "sha256": fp[r]["sha256"],
                "size": fp[r]["size"],
                "records": counts[r],
                "inserted": inserted[r],
                "skipped": skipped[r],
            }
            for r in ("item", "monster", "magic")
        },
        "errors": import_errors or errors,
    }
    write_manifest(manifest_doc)

    return {
        "ok": True,
        "rebuilt": True,
        "catalog_version": catalog_version,
        "db_path": str(DB_PATH),
        "record_counts": {
            "item": counts["item"],
            "monster": counts["monster"],
            "magic": counts["magic"],
        },
        "inserted": inserted,
        "skipped": skipped,
        "errors": {k: v for k, v in errors.items() if v},
    }


def _db_verified(catalog_version: str) -> bool:
    """Check the existing DB matches the declared catalog_version."""
    if not DB_PATH.exists():
        return False
    try:
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute(
            "SELECT catalog_version FROM manifest WHERE catalog_version = ?",
            (catalog_version,),
        ).fetchone()
        conn.close()
        return row is not None
    except sqlite3.Error:
        return False


def db_path() -> Path:
    """Public accessor used by the tool handler."""
    return DB_PATH


def latest_manifest() -> dict | None:
    """Return the in-DB manifest row as a dict (or None)."""
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM manifest ORDER BY imported_at_utc DESC LIMIT 1"
        ).fetchone()
        conn.close()
        return dict(row) if row else None
    except sqlite3.Error:
        return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Import Conan client catalog into SQLite.")
    ap.add_argument("--force", action="store_true", help="Rebuild even if sources unchanged.")
    args = ap.parse_args()
    result = import_catalog(force=args.force)
    print(json.dumps(result, indent=2, default=str))
