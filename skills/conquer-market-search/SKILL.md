---
name: conquer-market-search
version: 0.2.0
description: "Guidance for the read-only Conquer Online Classic market search tool (conquer_market_search) and the local client-data catalog tool (conquer_game_data_search)."
---

# Conquer Market Search

## When to use

Use the `conquer_market_search` tool for:

- Current Classic Conquer Online market listings
- Item availability checks
- Price checks
- Comparing listings returned by the API
- Searching a specified category, quality, subcategory, or plus level

## Rules

- This is read-only market lookup, not a buying or listing tool.
- Call `conquer_market_search` before claiming that an item is currently listed or quoting a current market price.
- Extract user-provided filters faithfully.
- Do not invent a server, category, quality, subcategory, plus level, or price.
- Use `server=0` only as the configured default when the user does not specify a server.
- If the requested query is too vague and broad results would not be useful, ask one focused follow-up question.
- State the filters used when presenting results.
- For "cheapest," inspect the actual returned JSON price field. Do not assume that `sort=4` or `direction=0` means lowest price until that is empirically confirmed from returned data.
- Distinguish facts returned by the API from interpretation, such as "this appears cheaper than the other returned listings."
- If there are no results, say no results were returned for the applied filters; do not say the item does not exist globally.
- If the API call fails, report the tool error and do not fabricate market data.

## Known request example

```json
{
  "server": 0,
  "category": "Boots",
  "subcategory": "Boots",
  "quality": "Fixed",
  "plus": 1,
  "sort": 4,
  "direction": 0,
  "page": 1,
  "page_size": 50
}
```

## Known values

Categories: Armor, Boots, Gem, Headgear, Necklace Bag, Others, Ring Bracelet, Valuables, Weapon.

Qualities: Elite, Fixed, Legendary, Normal, Refined, Super, Unique.

## Example user requests

- "Find +1 Fixed Boots on server 0."
- "Show me Elite weapons."
- "What Fixed Boots are listed right now?"
- "Compare the cheapest returned listings for +1 Boots."

---

## Local client-data catalog (`conquer_game_data_search`)

A second read-only tool, `conquer_game_data_search`, looks up static client
reference data (items, monsters, magic) from a local SQLite catalog built from
`itemtype.json`, `monster.json`, and `magictype.json`. It is exposed under the
same `conquer_market` toolset.

Input schema:

- `resource` (required): exactly `item`, `monster`, or `magic`.
- `query` (string): case-insensitive name substring. **Required unless `id`**
  is given.
- `id` (integer|null): exact numeric client ID — `item.id`, `monster.type`, or
  `magic.magic_type`. For magic, all rows for that `magic_type` (one per
  `level`) are returned.
- `limit` (integer, default 20, max 50): cap on returned rows.

### Local-data rules

1. **Use `conquer_game_data_search` to resolve ambiguity.** When a user says an
   item / monster / magic name that is generic (e.g. "Boots", "Thunder") or
   could map to many IDs (reinforcement variants, multi-level magic), call the
   tool with `query` first to enumerate the candidate IDs, then use the exact
   `id` for a precise follow-up lookup before citing any specific definition.

2. **Treat local client data as version-specific reference data.** It describes
   how the client keys and labels entities; it is pinned to the SHA-256 of the
   three source files (returned as `catalog_version`). The exact client build
   that produced the files is NOT recorded inside them.

3. **Do NOT treat it as proof of live-server state.** An entry existing in the
   catalog does not mean it is currently listed, tradeable, droppable, or
   enabled on any particular private server. Do not infer drop rates,
   availability, enabled content, or exact formulas from presence in the file.

4. **Keep two sources strictly separated.** Use `conquer_game_data_search` only
   to identify / look up static definitions, and `conquer_market_search` only
   for current listings and asking prices. When answering a market question,
   surface the live listing facts from `conquer_market_search` and label any
   static definition context that came from the local catalog as
   `local_client_catalog` — never conflate the two.

5. **Label data sources explicitly.** Every `conquer_game_data_search` response
   carries `source_type: "local_client_catalog"` and full `catalog_metadata`
   (version, hashes, record counts). Surface this metadata so the user can see
   it is reference data, not live server data.

6. **Respect duplicates and variants.** If a name maps to many IDs, present
   the candidate IDs and ask (or pick the most likely by context) rather than
   silently choosing one.

7. **When the catalog returns an error** (`catalog_unavailable`,
   `stale_source`, etc.), tell the user the local catalog is unavailable or
   out of date and must be rebuilt with `importer.py --force` — do not fall
   back to inventing client data.
