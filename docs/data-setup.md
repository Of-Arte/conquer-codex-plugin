# Data Setup

This plugin requires **local Conquer Online client reference files**. The market
search tool works out of the box (it hits a public API); the client-data catalog
tool requires you to provide these files.

## What you need

Three JSON files from a Classic Conquer 2.0 client installation:

| File              | Purpose              | What it contains                        |
|-------------------|----------------------|-----------------------------------------|
| `itemtype.json`   | Item definitions     | Item IDs, names, stats, requirements     |
| `monster.json`   | Monster definitions  | Monster types, names, levels, stats     |
| `magictype.json` | Magic/skill defs     | Spell IDs, names, levels, power, cost   |

## Where to find them

These files live inside your Classic Conquer 2.0 installation directory:

```
<Conquer install path>\Classic Conquer 2.0\ini\
```

For example, if you installed Conquer at `C:\Games\Conquer`:

```
C:\Games\Conquer\Classic Conquer 2.0\ini\itemtype.json
C:\Games\Conquer\Classic Conquer 2.0\ini\monster.json
C:\Games\Conquer\Classic Conquer 2.0\ini\magictype.json
```

> These are client-side reference files: they describe how the client labels
> items/monsters/magic. They are **not** proof of live server mechanics, drop
> rates, or availability. See [troubleshooting.md](troubleshooting.md).

## Where to put them

Copy the files into the plugin's local data source directory:

```bash
mkdir -p ~/.hermes/plugins/conquerCodex/data/source/
cp /path/to/your/itemtype.json   ~/.hermes/plugins/conquerCodex/data/source/
cp /path/to/your/monster.json    ~/.hermes/plugins/conquerCodex/data/source/
cp /path/to/your/magictype.json  ~/.hermes/plugins/conquerCodex/data/source/
```

## Build the catalog

Once the files are in place, build the SQLite catalog:

```bash
cd ~/.hermes/plugins/conquerCodex
python3 importer.py
```

**Idempotent:** re-running is a no-op if the source hashes haven't changed.

**Stale detection:** if you swap in new source files, the importer refuses to
run silently and asks you to use `python3 importer.py --force`.

**Output:** the catalog is written to
`~/.hermes/plugins/conquerCodex/data/catalog/conquer_client_catalog.sqlite3`.

## Verify it worked

```bash
# Check source fingerprints
python3 importer.py  # should say "catalog already current"

# Or query directly
python3 -c "
from importer import source_fingerprints, latest_manifest
print(source_fingerprints())
print(latest_manifest())
"
```

## No dependencies required

The importer uses only Python standard library: `json`, `hashlib`, `sqlite3`,
`pathlib`, `datetime`. No pip install needed.