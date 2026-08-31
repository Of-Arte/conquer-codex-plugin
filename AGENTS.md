# AGENTS.md — conquerCodex Plugin

> Guide for AI coding assistants and agents working on this Hermes plugin repo.

## What this plugin is

A Hermes profile-scoped standalone plugin providing two read-only tools for
Conquer Online Classic theorycrafting:

- `conquer_market_search` — live market listings via the public API
- `conquer_game_data_search` — local, version-pinned client reference data in a
  read-only SQLite catalog

Four companion skills guide how these tools are used:

- `conquerGameData` — local client-catalog entity lookup (conquer_game_data_search)
- `conquerMarketSearch` — live market listing queries and price snapshots
- `conquerTheorycraft` — evidence-hierarchical theorycrafting across sources
- `conquerReduxReference` — read-only reference-implementation investigation of
  the local Redux fork, with mandatory source classification and compatibility
  labels

## Version tracking

- The **plugin** version lives in `plugin.yaml` (`version:` field) and tracks
  tool, schema, and importer changes. The current plugin version is **0.3.0**.
- Each **skill** carries its own version in the YAML frontmatter of its
  `SKILL.md` (`version:` field). Bump a skill's version when its doctrine,
  evidence hierarchy, compatibility labels, or response format change.
- Skill versions evolve independently of the plugin version. It is normal for a
  skill version to be ahead of or behind the plugin version.
- Bump the plugin version when introducing new tools or changing the plugin
  manifest, `__init__.py` registration, or importer schema.
- Do NOT include version strings in README unless they describe the importer
  format version (e.g. `conquerCodex-importer-v1`).

## Commit template

Use this template for all commits to this repository:

```
<scope>: <short summary>

[optional body — up to ~72 chars per line]

- Bullet list of changes if multiple
- Be specific about what changed, not just "updated"

Fixes/Refs: #<issue>  (when applicable)

Verified:
- <verification step 1>
- <verification step 2>
```

### Scope conventions

- `v0.3.0` or `v<next>` — plugin version-bearing release commits
- `skills` — skill boundary / SKILL.md changes (including per-skill version bumps)
- `plugin` — __init__.py, plugin.yaml, registration changes
- `tools` — tool implementation (tools.py, schemas.py)
- `importer` — importer.py, catalog build changes
- `docs` — README.md, AGENTS.md, documentation-only changes

### Commit message style

- Lowercase lowercase except proper nouns and acronyms (Conquer, Hermes, SQLite,
  API, JSON)
- No trailing period on the subject line
- Wrap body at 72 characters
- Use the imperative mood ("Add" not "Added", "Fix" not "Fixed")

### Release process

1. Make changes
2. Verify syntax: `python3 -c "import py_compile; py_compile.compile('tools.py', doraise=True)"`
3. Verify plugin discovery: `hermes --profile conquer plugins list --plain --no-bundled`
4. Verify each affected skill loads:
   `hermes --profile conquer --skills conquerCodex:<skill> chat -q "test query"`
5. Bump the **skill** version in its `SKILL.md` frontmatter when its doctrine or
   evidence classification changes (commit scope: `skills`)
6. Bump the **plugin** version in `plugin.yaml` when tools, schemas, the
   manifest, or `__init__.py` registration changes (commit scope: `plugin`,
   `tools`, or `importer`)
7. Stage and commit using the template above
8. Push: `git push`

## Testing requirements

- Never commit raw client JSON, SQLite catalogs, cache files, or secrets
- Run direct tool tests and a fresh-session agent-level test after changes
- Do not present formulas or mechanics as target-server-confirmed without evidence
- The catalog is version-pinned reference data, not live server proof

## File layout

```
~/.hermes/profiles/conquer/plugins/conquerCodex/
├── plugin.yaml           # manifest + plugin version
├── __init__.py           # register() entrypoint: tools + skills
├── schemas.py            # tool input schemas
├── tools.py              # tool handlers
├── importer.py           # one-time SQLite build from raw JSON
├── README.md             # user-facing docs
├── AGENTS.md             # this file
├── .gitignore
└── skills/
    ├── conquerGameData/SKILL.md
    ├── conquerMarketSearch/SKILL.md
    ├── conquerReduxReference/SKILL.md
    └── conquerTheorycraft/SKILL.md
```
