"""conquer-market Hermes plugin.

Registers the ``conquer_market_search`` tool under the ``conquer_market``
toolset, plus a companion skill ``conquer-market:conquer-market-search``.

Hermes loads this plugin when enabled (via ``hermes plugins enable conquer-market``).
The plugin is intentionally minimal: one read-only tool + one skill, no MCP,
no extra dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path

from .schemas import CONQUER_MARKET_SEARCH
from .tools import conquer_market_search


def register(ctx) -> None:
    # Register the read-only market search tool.
    ctx.register_tool(
        name="conquer_market_search",
        toolset="conquer_market",
        schema=CONQUER_MARKET_SEARCH,
        handler=conquer_market_search,
        emoji="🛒",
    )

    # Register the companion skill so it is resolvable via
    # skill_view(name="conquer-market:conquer-market-search").
    skill_md = Path(__file__).resolve().parent / "skills" / "conquer-market-search" / "SKILL.md"
    if skill_md.exists():
        ctx.register_skill(
            name="conquer-market-search",
            path=skill_md,
            description="Guidance for using the read-only Conquer Online Classic market search tool.",
        )
