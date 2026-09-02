# Usage Guide

## Quick Start

After [installing](README.md#installation) and [setting up data files](data-setup.md):

```
# Market search (live API, no data files needed)
hermes chat -q "Find elite weapons on server 0"

# Client data lookup (requires catalog built)
hermes chat -q "What is item ID 111303?"
hermes chat -q "Search for IronHelmet items"
```

---

## Tool 1: conquer_market_search

Queries the public Conquer Online Classic market API. Read-only: no purchases
or listings submitted.

### Parameters

| Parameter    | Type             | Required | Default | Notes                           |
|-------------|------------------|----------|---------|---------------------------------|
| `server`    | integer          | No       | `0`     | Server ID                       |
| `category`  | string or null   | No       | null    | Armor, Boots, Gem, etc.         |
| `subcategory` | string or null | No       | null    | Weapon type (e.g. "Sword")      |
| `quality`   | string or null   | No       | null    | Elite, Fixed, Legendary, etc.   |
| `plus`      | integer or null  | No       | null    | Reinforcement level             |
| `page`      | integer          | No       | `1`     | Minimum 1                       |
| `page_size` | integer          | No       | `50`    | 1–50                            |
| `sort`      | integer          | No       | `4`     | Semantics not fully documented  |
| `direction` | integer          | No       | `0`     | 0=desc, 1=asc                   |

### Example requests

<details>
<summary>Find +1 Fixed Boots on server 0</summary>

```json
{"server": 0, "category": "Boots", "quality": "Fixed", "plus": 1}
```
</details>

<details>
<summary>Show Elite weapons sorted by price</summary>

```json
{"server": 0, "category": "Weapon", "quality": "Elite", "sort": 4, "direction": 1}
```
</details>

<details>
<summary>What's in the Valuables category?</summary>

```json
{"server": 0, "category": "Valuables", "page_size": 50}
```
</details>

### Categories

Armor, Boots, Gem, Headgear, Necklace Bag, Others, Ring Bracelet, Valuables, Weapon.

### Qualities

Elite, Fixed, Legendary, Normal, Refined, Super, Unique.

---

## Tool 2: conquer_game_data_search

Queries a local, read-only SQLite catalog built from client reference files.
See [data-setup.md](data-setup.md) for how to build it.

### Parameters

| Parameter | Type                | Required | Default | Notes                              |
|----------|---------------------|----------|---------|------------------------------------|
| `resource` | string (enum)   | **Yes**  | —       | `item`, `monster`, or `magic`      |
| `query`  | string              | No*      | —       | Case-insensitive name substring    |
| `id`     | integer             | No*      | —       | Exact client ID                    |
| `limit`  | integer             | No       | `20`    | Clamped to 1–50                    |

*Either `query` or `id` is required.

### Example requests

<details>
<summary>Look up an item by ID</summary>

```json
{"resource": "item", "id": 111303}
```
</details>

<details>
<summary>Search for items by name</summary>

```json
{"resource": "item", "query": "iron helmet", "limit": 10}
```
</details>

<details>
<summary>Look up a magic type by ID (all levels)</summary>

```json
{"resource": "magic", "id": 1}
```
</details>

<details>
<summary>Search monsters</summary>

```json
{"resource": "monster", "query": "pirate", "limit": 5}
```
</details>

---

## Companion Skills

This plugin bundles four skills that guide how the tools are used:

| Skill name                       | Access               | Purpose                                            |
|----------------------------------|----------------------|----------------------------------------------------|
| `conquerCodex:conquerMarketSearch` | `skill_view(name='conquerCodex:conquerMarketSearch')` | Live market listing queries and price snapshots |
| `conquerCodex:conquerGameData`     | `skill_view(name='conquerCodex:conquerGameData')`     | Local client-catalog entity lookup          |
| `conquerCodex:conquerTheorycraft`  | `skill_view(name='conquerCodex:conquerTheorycraft')`  | Evidence-hierarchical theorycrafting      |
| `conquerCodex:conquerReduxReference` | `skill_view(name='conquerCodex:conquerReduxReference')` | Redux fork reference investigation       |

---

## Test Prompts

1. "Find +1 Fixed Boots on server 0."
2. "Show me Elite weapons with sort by price."
3. "What items are listed under the Valuables category on server 0?"
4. "Look up item ID 111303 in the client catalog."
5. "Search for 'IronHelmet' items in the local catalog."

---

## Response Format

### Market search success

```json
{
  "ok": true,
  "endpoint": "https://api.conqueronline.net/api/public/market/items",
  "params": { "server": 0, "category": "Boots", "quality": "Fixed", "plus": 1, ... },
  "http_status": 200,
  "data": { "items": [...], "totalCount": N, "totalPages": N }
}
```

### Client data success

```json
{
  "ok": true,
  "source_type": "local_client_catalog",
  "catalog_version": "<sha256|sha256|sha256>",
  "catalog_metadata": { "importer_version": "conquerCodex-importer-v1", ... },
  "resource": "item",
  "results": [ { "id": 111303, "name": "IronHelmet", ... } ]
}
```

Errors return `ok: false` with an `error` object containing `type` and `message`.