---
name: conquerGameData
version: 0.1.0
description: Local Classic Conquer client-catalog lookup guidance.
---

# Conquer Game Data

## When to use

Use this skill only for local static client reference data returned by
`conquer_game_data_search`: item, monster, and magic names, IDs, variants, and
client-visible fields.

## Catalog rules

- Label catalog-derived results `local_client_catalog`.
- For an ambiguous entity, search by name first and present the matched
  candidates before selecting a record.
- Before citing a particular item, monster, or magic record, perform an exact ID
  lookup.
- Magic type IDs can return multiple levels or variants; identify every returned
  level or variant rather than treating an ID as a single record.
- Surface catalog version or other returned catalog metadata when material to
  the answer.
- The catalog is static local client reference data. Do not infer live
  availability, enabled content, drops, server formulas, or server mechanics
  from it.
- If the catalog tool returns an error, report that error honestly; do not
  fabricate data.

## Catalog-only response layout

Use only the sections that apply:

### Matched candidates
- Label `local_client_catalog` and list name-search candidates with their IDs
  and distinguishing fields.

### Exact lookup
- For a cited record, show the exact ID result and relevant client-visible
  fields. For magic, include returned levels or variants.

### Catalog metadata
- Include returned catalog version or metadata when material.

### Limitations
- State that the result is local static client reference data and does not
  establish live server availability, enablement, drops, formulas, or mechanics.
