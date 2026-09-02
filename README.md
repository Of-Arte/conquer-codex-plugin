# conquerCodex

A Hermes plugin providing two read-only tools for Conquer Online Classic
theorycrafting:

## Tools

1. **`conquer_market_search`**: live market listings via the public API
2. **`conquer_game_data_search`**: local client reference data in a read-only
   SQLite catalog

Neither tool buys, sells, authenticates, or makes state-changing requests.

## Installation

Clone into your Hermes plugins directory and enable:

```bash
git clone https://github.com/Of-Arte/conquer-codex-plugin.git \
  ~/.hermes/plugins/conquerCodex
hermes plugins enable conquerCodex
```

Verify:

```bash
hermes plugins list
hermes chat -q "Find elite weapons on server 0"
```

## Data Setup

The market search tool works immediately (no data files needed).

The client-data catalog tool requires your Classic Conquer 2.0 client
reference files. See [docs/data-setup.md](docs/data-setup.md) for full details.

Quick version:

1. Copy `itemtype.json`, `monster.json`, `magictype.json` from your
   Classic Conquer 2.0 `ini/` directory into the plugin's `data/source/` folder
2. Build the catalog: `cd ~/.hermes/plugins/conquerCodex && python3 importer.py`

## Usage

See [docs/usage.md](docs/usage.md) for full parameter tables and examples.

```
hermes chat -q "Find elite weapons on server 0"
hermes chat -q "What is item ID 111303?"
```

## Architecture

See [docs/architecture.mmd](docs/architecture.mmd) for a diagram of the
plugin's data flow and module seams.

## Companion Skills

The plugin bundles four skills (load via `skill_view(name='conquerCodex:<name>')`):

| Skill                | Purpose                                      |
|----------------------|----------------------------------------------|
| `conquerMarketSearch`  | Live market listing queries and price snapshots |
| `conquerGameData`     | Local client-catalog entity lookup           |
| `conquerTheorycraft`  | Evidence-hierarchical theorycrafting         |
| `conquerReduxReference` | Read-only Redux fork reference investigation |

## Troubleshooting

See [docs/troubleshooting.md](docs/troubleshooting.md) for common issues:
plugin not found, stale source errors, Cloudflare 403s, empty results, and
skill loading problems.

## Limitations

- **sort/direction semantics are not fully documented**: inspect returned
  `price` fields directly for comparisons
- **API response schema may change**: returned fields are not version-pinned
- **Catalog data is client reference only**: does not prove live server
  availability, drop rates, or mechanics
- **No state-changing operations**: read-only market lookup only
- **Client JSON files are not included**: must provide your own from your
  Classic Conquer 2.0 client installation

## License

[MIT](LICENSE).
