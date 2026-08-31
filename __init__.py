"""conquerCodex Hermes plugin.

Registers two read-only tools under the ``conquer_market`` toolset:

* ``conquer_market_search`` — queries the public Conquer Online Classic market
  API for current listings.
* ``conquer_game_data_search`` — local, read-only SQLite lookup over the client
  reference files (itemtype.json, monster.json, magictype.json).

Plus three companion skills accessible via ``conquerCodex:<skill>``:

* ``conquerMarketSearch`` — guidance for market listing queries and price snapshots.
* ``conquerGameData`` — guidance for local client-catalog entity lookup.
* ``conquerTheorycraft`` — evidence-hierarchical theorycrafting across sources.

Hermes loads this plugin when enabled (via ``hermes plugins enable
conquerCodex``). The plugin is intentionally minimal: two read-only tools
+ three skills, no MCP, no extra dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

from .schemas import CONQUER_GAME_DATA_SEARCH, CONQUER_MARKET_SEARCH
from .tools import conquer_market_search, conquer_game_data_search


def register(ctx) -> None:
    # Register the read-only market search tool.
    ctx.register_tool(
        name="conquer_market_search",
        toolset="conquer_market",
        schema=CONQUER_MARKET_SEARCH,
        handler=conquer_market_search,
        emoji="🛒",
    )

    # Register the read-only local client-data catalog tool.
    ctx.register_tool(
        name="conquer_game_data_search",
        toolset="conquer_market",
        schema=CONQUER_GAME_DATA_SEARCH,
        handler=conquer_game_data_search,
        emoji="📜",
    )

    # Register the companion skills so they are resolvable via
    # skill_view(name="conquerCodex:...") within the Conquer profile.
    #
    # - conquerMarketSearch: live market listing queries, price snapshots.
    # - conquerTheorycraft:  multi-source item/market comparison with the
    #   explicit evidence hierarchy (local catalog -> live market -> official
    #   sources -> labeled working theory). Orchestrates conquerGameData for
    #   entity resolution and hands off catalog procedure to it.
    for skill_name, skill_desc in (
        (
            "conquerMarketSearch",
            "Guidance for read-only Conquer Online Classic market listing queries and price snapshots.",
        ),
        (
            "conquerTheorycraft",
            "Evidence-hierarchical theorycrafting across the local client catalog, live market data, and official sources.",
        ),
        (
            "conquerGameData",
            "Local Classic Conquer client-catalog entity lookup guidance.",
        ),
        (
            "conquerReduxReference",
            "Read-only reference-implementation investigation guidance for the local Redux fork, with mandatory source classification, compatibility labels, and provenance recording.",
        ),
    ):
        skill_md = (
            Path(__file__).resolve().parent / "skills" / skill_name / "SKILL.md"
        )
        if skill_md.exists():
            ctx.register_skill(
                name=skill_name,
                path=skill_md,
                description=skill_desc,
            )
