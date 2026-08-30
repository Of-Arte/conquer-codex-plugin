"""Schemas for the conquer-market plugin tools.

All schemas are plain dicts in Hermes' expected JSON-Schema shape.
They are kept compact to minimize context bloat.
"""

from __future__ import annotations

# -- Enum-like validation tables --------------------------------------------
# These mirror the categories and qualities the public API advertises in its
# response metadata. They are used for input validation only — the API itself
# is the source of truth for what it returns.

KNOWN_CATEGORIES = {
    "Armor",
    "Boots",
    "Gem",
    "Headgear",
    "Necklace Bag",
    "Others",
    "Ring Bracelet",
    "Valuables",
    "Weapon",
}

KNOWN_QUALITIES = {
    "Elite",
    "Fixed",
    "Legendary",
    "Normal",
    "Refined",
    "Super",
    "Unique",
}

# -- Tool schema ------------------------------------------------------------

CONQUER_MARKET_SEARCH = {
    "name": "conquer_market_search",
    "description": (
        "Search the public Conquer Online Classic market API for current item "
        "listings. Use this for live listing availability, prices, and item "
        "comparisons. This is read-only. Filter by server, category, "
        "subcategory, quality, plus level, sorting, and page."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "server": {
                "type": "integer",
                "description": "Server ID (0-based index).",
                "default": 0,
            },
            "category": {
                "type": "string",
                "description": (
                    "Item category, e.g. 'Weapon', 'Armor', 'Boots'. "
                    "Must match a known category exactly. Omit for unfiltered search."
                ),
            },
            "subcategory": {
                "type": "string",
                "description": (
                    "Exact API-facing subtype, e.g. 'Sword' for Weapon. "
                    "Only sent when explicitly provided."
                ),
            },
            "quality": {
                "type": "string",
                "description": (
                    "Item quality: Elite, Fixed, Legendary, Normal, Refined, "
                    "Super, or Unique. Must match exactly."
                ),
            },
            "plus": {
                "type": "integer",
                "description": (
                    "Plus/Reinforcement level (non-negative integer). "
                    "Omitted from request when not supplied."
                ),
            },
            "page": {
                "type": "integer",
                "description": "Page number (1-based, minimum 1).",
                "default": 1,
            },
            "page_size": {
                "type": "integer",
                "description": "Results per page (1-50, max 50).",
                "default": 50,
            },
            "sort": {
                "type": "integer",
                "description": "Sort field (default 4). Semantics not fully documented.",
                "default": 4,
            },
            "direction": {
                "type": "integer",
                "description": "Sort direction (0=desc, 1=asc). Semantics not fully documented.",
                "default": 0,
            },
        },
        "required": [],
    },
}
