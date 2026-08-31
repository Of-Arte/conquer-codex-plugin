---
name: conquerTheorycraft
version: 0.5.0
description: "Evidence-synthesis theorycrafting for Classic Conquer Online."
---

# Conquer Theorycraft

Use this skill to synthesize evidence for **Classic Conquer Online**, a private
server based on the Conquer Online 1.0 era immediately before version 2.0. It
has a heavily customized 1.0 client, a custom 2.0-style UI, and server-specific
changes that can differ from historical retail 1.0 behavior. Do not equate a
client record, retail-era claim, implementation, or market listing with proof
of live target-server mechanics.

## When to use

Use for cross-source gameplay, item, monster, magic, build, or market questions
that require evidence weighting and a recommendation. For a single-filter live
market availability or price query, use `conquerCodex:conquerMarketSearch`
instead.

## Critical distinction: domains vs. evidence classification

A **domain** is a research target; an **evidence classification** is the
authority weight for one fetched page, post, guide, source file, or claim.
Classify content by its own provenance, not host alone. For example, a relevant
Classic Conquer wiki page can be `target_server_official`; a staff Discord post
can be `target_server_official`; player discussion in that Discord is
`target_server_community`; and a modern retail page on `co.99.com` remains
`modern_retail_reference`.

## Verified target-server domains

Preferred primary research targets:

```text
https://conqueronline.net
https://wiki.conqueronline.net
```

Classify a relevant Classic Conquer page from either as
`target_server_official`, provided it is actually about Classic Conquer rather
than unrelated, stale, or archival content hosted there.

Verified aliases/supporting hosts:

```text
https://conquer.online
https://classic.conqueronline.net
https://classic2.conqueronline.net
https://download.conqueronline.net
```

Do not make aliases primary targets. Use one only when it is a final redirect
from a primary domain, directly supplied by the user, or directly linked by a
primary domain. Classify its content from the page evidence, not its host.

### Excluded domain

```text
https://classicconqueronline.com
```

Classify as `excluded_unrelated_server`. It is a different private server:
never query or use it as Classic Conquer evidence, or to infer mechanics,
economy, content availability, patches, population, or client behavior.

## Evidence taxonomy

### `target_server_official`

Relevant official Classic Conquer website/wiki pages and verified staff,
admin, or moderator posts in the official Classic Conquer Discord: announcements,
changelogs, rules, guides, FAQs, store/help pages, and server documentation.
This is the strongest public evidence for current mechanics, enabled content,
events, rules, and server-specific behavior. A first-party host by itself is
not enough when the page is unrelated, stale, archival, or not Classic Conquer.

### `target_server_community`

Ordinary player discussion in official Classic Conquer Discord and player-made
guides, strategy threads, anecdotes, or observations in target-server spaces.
Use only for strategy leads, player-experience context, and hypotheses—not as
standalone proof of mechanics, drop rates, formulas, or official policy.

### `local_client_catalog`

Version-pinned local client records returned by `conquer_game_data_search`:
item, monster, and magic IDs, variants, names, and client-visible fields.
It supports entity resolution, not proof of live enablement, drop rates,
hidden formulas, availability, or current mechanics.

**Catalog handoff:** use `conquerCodex:conquerGameData` for the full
local-catalog procedure — name-first ambiguity resolution, exact ID lookup,
variant handling, catalog metadata, and error reporting. Label results
`local_client_catalog` and do not treat them as live-server proof.

### `target_server_market`

Current public-market listings from `conquer_market_search`
(`https://api.conqueronline.net/api/public/market/items`). Use for listing,
availability-snapshot, and asking-price observations only; it does not prove
completed sales, durable price history, or mechanics.

### `historical_pre_2_0_reference`

Conquer Online material plausibly tied to the 1.0 or immediately pre-2.0 era,
including dated, relevant pre-2.0 `co.99.com` guides/news/archived documentation
and `bbs.co.99.com` forum posts **when the page itself establishes its date,
version, and relevant context**. Use for historical terminology, gameplay
context, build-era mechanics leads, and historical forum/guidance where Classic
Conquer has no verified first-party forum.

Classify each page, not its domain. Historical compatibility with customized
Classic Conquer is unconfirmed unless corroborated by `target_server_official`
evidence or `local_client_catalog` data. Do not use historical retail
databases for entity resolution when the local client catalog can provide the
version-pinned record.

### `modern_retail_reference`

Official `co.99.com` or retail Conquer content that is post-2.0, modern, or
mismatched to the target build—for example later classes, modern patches/events,
cross-server systems, modern economy, or current retail content. Use only for
explicit retail comparison or background; default relevance is
`likely_retail_only`. Do not silently apply it to Classic Conquer mechanics.

A relevant, dated pre-2.0 `co.99.com` or `bbs.co.99.com` page is
`historical_pre_2_0_reference`, not modern retail merely because of its host.
Conversely, modern or mismatched retail content on either host is
`modern_retail_reference`.

### `community_reference`

RageZone, Elitepvpers, unaffiliated forums/wikis, videos, Reddit, fan sites,
and third-party guides. Use only as implementation/history leads or strategy
hypotheses; independently verify before presenting a claim as target-server
fact.

### `reference_implementation`

The local version-controlled Redux fork at `workspace/Redux-Conquer-Online-Server`
and other open-source emulator/server implementations. Use only as candidate
implementation/formula references. Record the relevant files, repository,
commit, and working-tree state; audit the actual code path rather than names or
comments. If relevant files are modified, say the result is from the local
working tree. Without that provenance, omit the claim rather than relabeling it.

For the detailed step-by-step procedure when inspecting Redux code, apply the
`conquerCodex:conquerReduxReference` skill. It carries the read-only repository
policy, provenance-recording checklist, and the exact compatibility-label set
used when a Redux finding enters a theorycraft conclusion.

Redux is not target-server evidence and does not prove Classic Conquer shares
its implementation. A client catalog record cannot corroborate a
Redux-derived server formula. Treat conclusions as working theory unless
`target_server_official` corroborates them.

### `excluded_unrelated_server`

`classicconqueronline.com` and any other verified different private server.
Never use this classification as evidence; exclude it from target-server
searches and conclusions.

## Compact cross-source workflow

1. **Resolve entities.** If terminology, IDs, qualities, or variants are
   ambiguous, use `conquerCodex:conquerGameData` first. Completion: resolved
   records or a clearly labeled `local_client_catalog` failure.
2. **Establish target-server facts.** When mechanics, rules, enabled content,
   or current status matter, fetch relevant evidence from verified target-server
   sources first and classify each page/post. Completion: official evidence or
   an explicit statement that it was not found.
3. **Add live market evidence only when material.** Query
   `conquer_market_search` only if current listings or prices affect the
   question. Label it `target_server_market` and record the exact filters,
   result count, and observed asking prices.
4. **Use lower-authority context carefully.** Use dated historical content,
   target-server community content, modern retail material, community references,
   and reference implementations only with their taxonomy labels and stated
   constraints. Discord must be user-provided, publicly accessible through an
   approved source, or directly linked by a verified target-server page; classify
   staff and player content separately. When a `reference_implementation`
   question requires repository inspection, delegate to
   `conquerCodex:conquerReduxReference` for the provenance and read-only policy.
5. **Synthesize before recommending.** Separate verified facts, assumptions,
   and working theory. Completion: a direct recommendation that identifies the
   evidence label supporting it and the uncertainty that could change it.

## Response format

Use only the sections relevant to the question.

### Target-server evidence
- Cite relevant pages/posts and label each `target_server_official` or
  `target_server_community`. Explicitly say when official evidence is absent.

### Local client reference
- Give matched IDs, variants, relevant client-defined fields, and catalog
  metadata when relevant. Label `local_client_catalog`.

### Current Classic Conquer market snapshot
- Include only when queried. Label `target_server_market`; state exact filters,
  result count, and observed asking prices.

### Historical or external reference
- Label each claim `historical_pre_2_0_reference`, `modern_retail_reference`,
  `community_reference`, `reference_implementation`, or
  `excluded_unrelated_server` as applicable. Do not use excluded sources as
  evidence.

### Facts, assumptions, and working theory
- Distinguish confirmed target-server facts from client-reference facts,
  assumptions, and hypotheses.

### Direct conclusion and uncertainty
- Give the recommendation plainly. Name the specific uncertainty that could
  change it, such as an unrecorded server customization or absent staff
  confirmation of a mechanic.

## Known market values

Categories: Armor, Boots, Gem, Headgear, Necklace Bag, Others, Ring Bracelet,
Valuables, Weapon.

Qualities: Elite, Fixed, Legendary, Normal, Refined, Super, Unique.

## Verification checklist (do not distribute to users)

1. Confirm `conquerCodex:conquerTheorycraft`, `conquerCodex:conquerGameData`,
   `conquerCodex:conquerMarketSearch`, and `conquerCodex:conquerReduxReference`
   all load (`skill_view(name='...')`).
2. Run a no-write question involving a known local entity and a live market
   lookup when current market data is relevant.
3. Confirm labels distinguish `local_client_catalog`, `target_server_market`,
   and `target_server_official`, and that no excluded or inappropriate modern
   retail source was used.
4. Confirm Redux-derived findings are routed through `conquerReduxReference`
   with `reference_implementation` labeling, provenance recording, and a
   compatibility label.
5. Do not write persistent memory from the test.
