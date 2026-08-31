# conquerCodex

A Hermes plugin providing two read-only tools for Conquer Online Classic theorycrafting:

1. `conquer_market_search` — live market listings via the public API.
2. `conquer_game_data_search` — local, version-pinned client reference data (item definitions, monster stats, and magic/skill definitions) materialized into a read-only SQLite catalog.

Neither tool buys items, submits listings, authenticates as a player, scrapes browser pages, or makes any state-changing request.

## What it does

This plugin exposes a single deterministic read-only tool, `conquer_market_search`, which queries the public Classic Conquer Online market API and returns the current item listings as structured JSON. It is useful for checking live listing availability, prices, and comparing items. It does **not** buy items, submit listings, authenticate as a player, scrape browser pages, or make any state-changing request.

## Fixed public endpoint

```
GET https://api.conqueronline.net/api/public/market/items
```

## Tool parameters and validation

| Parameter | Type | Required | Default | Notes |
|---|---|---|---|---|
| `server` | integer | No | `0` | Server ID |
| `category` | string or null | No | null | Validated against known categories when supplied |
| `subcategory` | string or null | No | null | Exact API-facing subtype when supplied |
| `quality` | string or null | No | null | Validated against known qualities when supplied |
| `plus` | integer or null | No | null | Non-negative integer only; omitted when absent |
| `page` | integer | No | `1` | Must be >= 1 |
| `page_size` | integer | No | `50` | Must be 1-50 (max 50) |
| `sort` | integer | No | `4` | Semantics not fully documented |
| `direction` | integer | No | `0` | Semantics not fully documented |

**Known categories:** Armor, Boots, Gem, Headgear, Necklace Bag, Others, Ring Bracelet, Valuables, Weapon.

**Known qualities:** Elite, Fixed, Legendary, Normal, Refined, Super, Unique.

Invalid enum values, out-of-range integers, or non-integer types return structured error JSON. Null/omitted optional filters are excluded from the API request (never sent as literal `"null"`).

### Response shape

```json
{
  "ok": true,
  "endpoint": "https://api.conqueronline.net/api/public/market/items",
  "params": { ... },
  "http_status": 200,
  "data": { "items": [...], "totalCount": N, "totalPages": N, ... }
}
```

Errors return `ok: false` with an `error` object containing `type`, `message`, and optionally `body_preview`.

This is a **local Hermes plugin** installed at:

```
~/.hermes/plugins/conquerCodex/
```

File layout:

```
~/.hermes/plugins/conquerCodex/
├── plugin.yaml
├── __init__.py
├── schemas.py
├── tools.py
├── importer.py
├── README.md
└── skills/
    ├── conquerMarketSearch/
    │   └── SKILL.md          # live market listing queries & price snapshots
    ├── conquerGameData/
    │   └── SKILL.md          # local client-catalog entity lookup guidance
    └── conquerTheorycraft/
        └── SKILL.md          # multi-source item/market comparison + evidence hierarchy
```

After enabling, both tools appear under the `conquer_market` toolset
(`conquer_market_search` with emoji 🛒, `conquer_game_data_search` with emoji
📜). Three companion skills are bundled:

- `conquerMarketSearch` — live market listing queries, price snapshots, and
  use of `conquer_market_search`. Accessible via
  `skill_view(name='conquerCodex:conquerMarketSearch')`.
- `conquerGameData` — local client-catalog entity lookup guidance using
  `conquer_game_data_search`. Accessible via
  `skill_view(name='conquerCodex:conquerGameData')`.
- `conquerTheorycraft` — evidence-hierarchical theorycrafting that
  cross-references the local client catalog, live market data, and official
  sources. Accessible via
  `skill_view(name='conquerCodex:conquerTheorycraft')`.

## How to enable and verify

```bash
# Enable the plugin
hermes plugins enable conquerCodex

# Verify discovery
hermes plugins list
hermes plugins show conquerCodex

# Run the doctor
hermes plugins doctor conquerCodex
```

After enabling, the tool appears as `conquer_market_search` under the `conquer_market` toolset. The companion skill is accessible via `skill_view(name='conquerCodex:conquerMarketSearch')`.

## Test prompts

1. "Find +1 Fixed Boots on server 0."
2. "Show me Elite weapons with sort by price."
3. "What items are listed under the Valuables category on server 0?"

## Known limitations

- **`sort` and `direction` meanings are not fully documented/verified.** The API returns data sorted by `sort=4, direction=0`, but whether this reliably means "lowest price" is not confirmed. Inspect the returned `price` fields directly for price comparisons.
- **API response schema may change.** The current response includes `items`, `categories`, `qualities`, `servers`, `page`, `pageSize`, `totalCount`, `totalPages`. These fields are not version-pinned.
- **Read-only only.** This plugin does not support purchasing, listing, or any state-changing operation.
- **Zero returned listings does not mean global nonexistence.** An empty `items` array only means no listings matched the given filters on the given server.
- **API rate limits and terms of service should be respected.** One HTTP request per tool call with a 15-second timeout. A single retry is performed for transient network errors only.

---

## 2. Local client-data catalog — `conquer_game_data_search`

A second read-only tool queries a **local, version-pinned** SQLite catalog built from the client reference files `itemtype.json`, `monster.json`, and `magictype.json`. These files are reference data only — they describe how the client identifies items/monsters/magic and are **not** proof of live server mechanics, drop rates, availability, enabled content, or server-authoritative formulas.

### Directory layout

This is a **profile-scoped Hermes plugin**. The Hermes convention resolves plugin-owned data to `<profile>/plugin-data/<plugin-id>/`:

```
~/.hermes/profiles/conquer/
├── plugins/conquerCodex/        # the plugin package (git-tracked)
│   ├── __init__.py
│   ├── schemas.py
│   ├── tools.py
│   ├── importer.py                # one-time, stdlib-only SQLite importer
│   ├── plugin.yaml
│   └── skills/conquerMarketSearch/SKILL.md
└── plugin-data/conquerCodex/    # runtime data (NOT git-tracked)
    ├── source/                    # raw reference JSON (read-only, never modified by importer)
    │   ├── itemtype.json
    │   ├── monster.json
    │   └── magictype.json
    ├── catalog/
    │   └── conquer_client_catalog.sqlite3
    └── manifests/
        └── import-manifest.json
```

### Building the catalog

The catalog is built by running the importer (standard library only — `json`, `hashlib`, `sqlite3`):

```bash
cd ~/.hermes/profiles/conquer/plugins/conquerCodex
python3 importer.py            # build or verify
python3 importer.py --force    # rebuild even if sources unchanged
```

Behaviour:
* Idempotent: reruns are no-ops when the three source SHA-256 hashes are unchanged.
* Stale detection: if the sources changed since the last build, `import_catalog(force=False)` **refuses** to run and returns `ok: false, error.type: "stale_source"`. Use `--force` (or `force=True` from code) to rebuild.
* The catalog version is the concatenation `sha256(itemtype)|sha256(monster)|sha256(magictype)`, so any change to the raw data automatically invalidates cached catalogs.
* Invalid records are skipped and reported, not fatal.
* Raw source files are never modified.

### Tool parameters

```json
{
  "resource": "item | monster | magic",
  "query": "string (case-insensitive substring on name) — required unless id given",
  "id": 12345,
  "limit": 20
}
```

* `resource` is an enum: `item`, `monster`, or `magic`.
* At least one of `query` or `id` is required.
* `id` is the exact numeric client ID: `item.id`, `monster.type`, or `magic.magic_type` (magic matches all levels because `magic` rows are keyed by the composite `(magic_type, level)`).
* `limit` defaults to 20 and is clamped to 1–50.

### Success shape

```json
{
  "ok": true,
  "source_type": "local_client_catalog",
  "catalog_version": "<sha256|sha256|sha256>",
  "catalog_metadata": {
    "source_type": "local_client_catalog",
    "catalog_version": "...",
    "importer_version": "conquerCodex-importer-v1",
    "imported_at_utc": "2026-08-30T18:53:49Z",
    "record_counts": { "item": 11142, "monster": 374, "magic": 610 },
    "sources": {
      "item":    { "sha256": "...", "size": 8308073, "records": 11142 },
      "monster": { "sha256": "...", "size": 110420,  "records": 374 },
      "magic":   { "sha256": "...", "size": 591313,  "records": 610 }
    },
    "present": true
  },
  "resource": "item",
  "query": null,
  "id": 111303,
  "count": 1,
  "limit": 20,
  "results": [ { "id": 111303, "name": "IronHelmet", "required_level": 15, ... } ]
}
```

### Error shape

```json
{
  "ok": false,
  "source_type": "local_client_catalog",
  "catalog_version": "...",
  "catalog_metadata": { ... },
  "error": { "type": "validation_error", "message": "A query or id is required." }
}
```

Error types: `validation_error`, `catalog_unavailable`, `catalog_error`, `stale_source`, `missing_source`.

### Known limitations

- **Data is version-specific client reference data.** The exact client build that produced these files is not recorded inside the files; the catalog version is derived from their SHA-256 hashes instead.
- **Duplicate / variant rows are preserved.** Item names like `IronHelmet` map to many consecutive IDs (reinforcement / +level variants). `MagicType` rows repeat across `Level` 0–9, and some magic names map to multiple distinct `MagicType` IDs. Search returns the underlying records; treat the ID as the authoritative key.
- **`description`/`Disc` fields carry quality cues only loosely.** `itemtype.description == "Fixed"` is a coarse quality marker; `magictype.Disc` holds upgrade-tier strings. These are not a normalized quality system.
- **No server-state claims.** An item existing in `itemtype.json` does **not** mean it is currently listed, tradeable, droppable, or enabled on any specific private server. Cross-check with `conquer_market_search` for live listings.

