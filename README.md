# conquer-market

A Hermes plugin providing read-only access to the public Conquer Online Classic market API.

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

## Installation / discovery path

This is a **local Hermes plugin** installed at:

```
~/.hermes/plugins/conquer-market/
```

File layout:

```
~/.hermes/plugins/conquer-market/
├── plugin.yaml
├── __init__.py
├── schemas.py
├── tools.py
├── README.md
└── skills/
    └── conquer-market-search/
        └── SKILL.md
```

## How to enable and verify

```bash
# Enable the plugin
hermes plugins enable conquer-market

# Verify discovery
hermes plugins list
hermes plugins show conquer-market

# Run the doctor
hermes plugins doctor conquer-market
```

After enabling, the tool appears as `conquer_market_search` under the `conquer_market` toolset. The companion skill is accessible via `skill_view(name='conquer-market:conquer-market-search')`.

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
