---
name: conquerReduxReference
version: 0.1.0
description: Read-only reference-implementation investigation guidance for the local Redux fork, with mandatory source classification, compatibility labels, and provenance recording.
---

# Conquer Redux Reference

## When to use

Use this skill when:

- A theorycraft question needs a possible server-side implementation or formula.
- A local client-catalog record has a field whose purpose needs investigation.
- An item, monster, magic, packet, database record, or type ID needs tracing
  through an implementation.
- Target-server official documentation does not explain a mechanic.
- A user explicitly asks how Redux implements something.
- Hermes needs to compare a Redux implementation against Classic Conquer local
  client data or verified target-server evidence.

Do not use it for:

- Simple current-market questions.
- Basic name/ID resolution already answered by `conquerGameData`.
- Claims about current Classic Conquer behavior without corroboration.
- General web research.
- Editing, building, debugging, or operating the Redux server.

## Source classification

All evidence from the local Redux fork must be classified exactly as:

```text
reference_implementation
```

It is not:

```text
target_server_official
target_server_market
local_client_catalog
historical_pre_2_0_reference
modern_retail_reference
community_reference
```

## Repository

The local Redux fork lives at:

```text
~/.hermes/profiles/conquer/workspace/Redux-Conquer-Online-Server
```

This is a Git working tree. Before making any Redux-derived claim, record:

- Repository identity/path (safe local identity only — see read-only policy below).
- Current branch.
- Current commit hash.
- Relevant file paths inspected.
- Relevant symbols inspected (class, function/method, constant, SQL query,
  configuration key, database table/model, packet/type handler, formula expression).

## Read-only repository policy

Before making a Redux-derived claim, Hermes must record the provenance:

- Repository identity/path, unless revealing the path would expose sensitive
  local information.
- Current branch.
- Current commit hash.
- Relevant file paths inspected.
- Relevant symbols inspected:
  - class
  - function/method
  - constant
  - SQL query
  - configuration key
  - database table/model
  - packet/type handler
  - formula expression

Hermes may use safe read-only commands and tools such as:

```bash
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git remote -v
git status --short
find . -maxdepth 2 -type f
grep -RIn
rg
sed -n
head
tail
```

Constraints:

- Redact remote credentials if present.
- Do not run destructive Git commands.
- Do not modify tracked or untracked files.
- Do not run code from the repository.
- Do not run setup, package installation, migrations, containers, servers,
  tests, or database access.
- Do not inspect secrets or credentials.
- Prefer exact symbol/file inspection over broad repository dumping.
- Avoid returning large source files verbatim; summarize relevant logic and
  quote only small necessary excerpts when appropriate.

## Compatibility labels

Every conclusion based on Redux must use exactly one compatibility label:

```text
confirmed_target_server_match
client_correlated_only
plausible_implementation_candidate
unknown_compatibility
contradicted_by_target_server_evidence
```

Apply them as follows:

### confirmed_target_server_match

Use only when verified Classic Conquer target-server evidence or repeatable
user-provided in-game testing directly supports the same behavior.

### client_correlated_only

Use when the Redux behavior maps coherently to the configured local Classic
Conquer client catalog, but target-server server-side behavior remains
unverified.

### plausible_implementation_candidate

Use when Redux provides a reasonable model for a behavior or formula, but
there is no direct target-server or local-client corroboration.

### unknown_compatibility

Use when the code exists but there is insufficient evidence to relate it to
Classic Conquer.

### contradicted_by_target_server_evidence

Use when verified Classic Conquer server documentation, staff evidence, or
repeatable user-provided in-game evidence conflicts with Redux.

## Evidence hierarchy

When a theorycraft question uses multiple evidence sources, apply this order:

1. `target_server_official`
   - Verified Classic Conquer server website, Wiki, changelog, staff post,
     rules, or announcement.

2. `target_server_market`
   - `conquer_market_search` output from the Classic Conquer market API.
   - Use only for current listings and asking-price snapshots.

3. `local_client_catalog`
   - `conquer_game_data_search`.
   - Use for exact IDs, variants, client-visible fields, and terminology.

4. `reference_implementation`
   - The local Redux fork.
   - Use for possible implementation/formula behavior only.

5. `historical_pre_2_0_reference`
   - Historical Conquer 1.0/pre-2.0 material.

6. `modern_retail_reference`
   - Modern retail Conquer material.

7. `community_reference`
   - RageZone, Elitepvpers, Reddit, videos, player guides, etc.

Redux must not override verified target-server evidence.

## Required response format

When Redux is used in an answer, include this section when relevant:

```md
## Reference implementation

- Source: `reference_implementation`
- Repository: [safe local identity/path if appropriate]
- Branch: [branch]
- Commit: [full or short commit hash]
- Files and symbols inspected:
  - [path] — [symbol]
- Direct Redux behavior:
  - [what the code directly does]
- Compatibility:
  - [one required compatibility label]
- Classic Conquer applicability:
  - [what confirms, limits, or contradicts applicability]
```

Keep the distinction explicit:

- "Redux directly implements..."
- "Classic Conquer evidence confirms..."
- "Working theory: Classic Conquer may..."

Do not collapse those statements into one claim.

## Tool coordination

- Use `conquerGameData` first when the entity name, item ID, monster ID,
  magic ID, quality, reinforcement, or variant is ambiguous.
- Use `conquerMarketSearch` only when current Classic Conquer market
  availability or asking price matters.
- Use target-server official sources before Redux when a target-server
  mechanics/rules source is available.
- Use Redux only for the implementation question that remains unresolved.

## Verification checklist (do not distribute to users)

1. Confirm the skill loads (`skill_view(name='conquerMarket:conquerReduxReference')`).
2. Run a no-write question involving the Redux fork; confirm the response
   labels the source as `reference_implementation`, applies exactly one
   compatibility label, and does not claim Redux behavior is proven
   Classic Conquer behavior.
3. Confirm no Redux server, build, migration, test, or database action was run.
4. Confirm no secrets, credentials, or `.env` files were accessed.
5. Do not write persistent memory from the test.
