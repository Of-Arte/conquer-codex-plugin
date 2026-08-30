---
name: conquer-market-search
version: 0.1.0
description: "Guidance for using the read-only Conquer Online Classic market search tool (conquer_market_search)."
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
