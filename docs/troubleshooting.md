# Troubleshooting

## Plugin not found after install

```bash
# Verify plugin directory exists
ls ~/.hermes/plugins/conquerCodex/

# Verify Hermes can see it
hermes plugins list

# If listed but disabled, enable it
hermes plugins enable conquerCodex

# Debug discovery (verbose)
HERMES_PLUGINS_DEBUG=1 hermes plugins list
```

## "The local client-data catalog has not been built yet"

You need to:
1. Copy your client JSON files into `data/source/`, see
   [data-setup.md](data-setup.md)
2. Run the importer: `cd ~/.hermes/plugins/conquerCodex && python3 importer.py`
3. Re-run your query

## "Source files have changed since the last import" (stale_source error)

The SHA-256 hashes of your source files don't match the last import. Either:
- You swapped the JSON files for different client versions
- The files were modified

Force a rebuild:

```bash
cd ~/.hermes/plugins/conquerCodex
python3 importer.py --force
```

This rebuilds the catalog from the current source files.

## API returns HTTP 403 / "browser_signature_banned"

The Conquer Online API is behind Cloudflare and may reject requests that look
like bots. The plugin sets a browser-like User-Agent header by default. If
you're still blocked:

- **Try `curl` first** to confirm the endpoint is reachable:
  ```bash
  curl "https://api.conqueronline.net/api/public/market/items?server=0&page=1&pageSize=1"
  ```
- **Wait and retry**: Cloudflare's bot detection can be temporary.
- **Rate limit**: the API allows one request per tool call with a single retry.
  Don't spam the endpoint.

## Empty results from market search

An empty `items` array means no listings matched your filters on that server —
not that the item doesn't exist globally. Try:
- Different server ID (`server=1`, `server=2`, etc.)
- Broadening filters (remove `quality`, `plus`, `subcategory`)
- Checking the category spelling (case-insensitive but must be exact:
  "Weapon" not "weapons")

## "Unknown category 'X'"

You passed a subcategory as the category. Categories are parent buckets only
(e.g. `Weapon`). Weapon types like `Bow`, `Sword`, `Club` must go in the
`subcategory` field.

```json
{"category": "Weapon", "subcategory": "Bow"}  // correct
{"category": "Bow"}                            // error
```

## Catalog tool returns wrong data

Verify your source files:

```bash
cd ~/.hermes/plugins/conquerCodex
python3 -c "from importer import source_fingerprints; print(source_fingerprints())"
```

Confirm the SHA-256 hashes match the client version you expect. If someone
else's client files were accidentally copied, the catalog will have wrong
data.

## Skill not loading

Skills are bundled with the plugin. They load when the plugin is enabled:

```bash
# Check if the plugin is enabled
hermes plugins list

# Test skill loading
hermes --skills conquerCodex:conquerMarketSearch chat -q "test"
```

## Still stuck?

1. Check the [architecture diagram](architecture.mmd) for the data flow
2. Verify your Hermes version: `hermes --version`
3. Run the plugin doctor: `hermes plugins doctor conquerCodex`
