---
name: notion-cli
slug: notion-cli
version: 2.1.1
description: "Notion operations via the official Notion CLI (ntn). Use when (1) searching pages/databases, (2) querying or creating database entries, (3) reading or writing page content, (4) appending blocks, (5) managing comments, (6) deploying Notion Workers, (7) uploading files. Authenticated via keychain or NOTION_API_TOKEN."
metadata: {"clawdbot":{"emoji":"📝","requires":{"env":["NOTION_API_TOKEN"]},"os":["linux","darwin","win32"]}}
---

# notion-cli

Binary: `ntn` at `~/.local/bin/ntn` (ensure `PATH` includes it). Current version: 0.15.0.  
Auth: `ntn login` (browser flow, OS keychain) or `NOTION_API_TOKEN` env var.

## Pre-flight

```bash
export PATH="$HOME/.local/bin:$PATH"
ntn doctor                    # Verify setup and auth
ntn --version                 # Check installed version (should be ≥0.15.0)
ntn update                    # Self-update to latest
```

> ⚠️ `ntn update` may report success without actually replacing the binary (known bug in 0.14.0→0.15.0). If version stays old, manually download:
> ```bash
curl -fsSL "https://ntn.dev/releases/$(curl -fsSL https://ntn.dev/latest.txt)/ntn-x86_64-unknown-linux-musl.tar.gz" | tar -xzf - --strip-components=1 -C ~/.local/bin ntn-x86_64-unknown-linux-musl/ntn
```

If auth fails:
```bash
ntn doctor                    # Check which token ntn is actually using
ntn logout && ntn login       # Re-authenticate via browser flow
```

For file-based auth instead of OS keychain:
```bash
NOTION_KEYRING=0 ntn login    # Writes ~/.config/notion/auth.json
```

> ⚠️ Legacy token at `~/.config/notion/api_key` may be expired. `ntn` manages its own token in the OS keychain or `auth.json` — do not rely on the legacy file.

## Discover API endpoints

```bash
ntn api ls                    # List all available endpoints
ntn api v1/pages --docs       # Show official markdown docs for endpoint
ntn api v1/pages --spec       # Show reduced OpenAPI fragment
```

## Search

```bash
ntn api v1/search -d '{"query":"<query>"}'
ntn api v1/search -d '{"query":"Agent","page_size":5}' | jq '.results[] | .id, .url'
```

## Pages

### Read page
```bash
ntn api v1/pages/<page-id>
ntn api v1/pages/<page-id> | jq '.properties.Name.title[0].text.content'
```

### Read page content (blocks)
```bash
ntn api v1/blocks/<page-id>/children
ntn api v1/blocks/<page-id>/children page_size:=100
```

### Create page (workspace root)
```bash
ntn api v1/pages -d '{
  "parent": {"type":"workspace","workspace":true},
  "properties": {"title":{"title":[{"text":{"content":"New Page"}}]}}
}'
```

### Create page in database
```bash
ntn api v1/pages -d '{
  "parent": {"database_id":"<db-id>"},
  "properties": {
    "Name": {"title":[{"text":{"content":"New Entry"}}]},
    "Status": {"select":{"name":"Todo"}},
    "Tags": {"multi_select":[{"name":"urgent"}]}
  }
}'
```

### Update page properties
```bash
ntn api v1/pages/<page-id> -X PATCH -d '{
  "properties": {
    "Status": {"select":{"name":"Done"}},
    "Completed": {"checkbox":true}
  }
}'
```

### Archive / unarchive
```bash
ntn api v1/pages/<page-id> -X PATCH -d '{"archived":true}'
ntn api v1/pages/<page-id> -X PATCH -d '{"archived":false}'
```

## Inline body syntax (no JSON quoting)

The killer feature of `ntn api` — assign body fields directly from the shell:

```bash
# Create page with inline fields
ntn api v1/pages \
  parent[page_id]=abc123 \
  properties[Name][title][0][text][content]="Hello from CLI"

# Update checkbox
ntn api v1/pages/abc123 -X PATCH archived:=true

# Query with filter inline
ntn api v1/databases/xyz/query \
  filter[property]=Status \
  filter[select][equals]=Done

# Assign numbers, booleans, arrays with :=
ntn api v1/pages/abc123 -X PATCH properties[Count][number]:=42
```

Syntax rules:
- `path=value`       → JSON string assignment
- `path:=json`       → Typed assignment (number, bool, array, object)
- `name==value`      → Query parameter
- `Header:Value`     → Request header

## Data Sources & Databases

> ⚠️ **API Change (Sept 2025):** Notion moved `properties` from database-level to **data source** level. Querying via `ntn api v1/databases/<id>/query` returns `invalid_request_url`. Use `ntn datasources query` or `ntn api v1/data_sources/<id>/query` instead.

### Get database schema (list data sources)

```bash
ntn api v1/databases/<db-id>               # Returns data_sources array only
ntn api v1/databases/<db-id> | jq '.data_sources[] | {id, name}'
```

### Get data source schema (properties)

```bash
ntn api v1/data_sources/<data-source-id>   # Returns properties (columns)
ntn api v1/data_sources/<data-source-id> | jq '.properties | keys'
```

### Query data source (modern way)

```bash
# Simple query via CLI helper
ntn datasources query <data-source-id> --limit 50 --json

# With filter
ntn datasources query <data-source-id> --filter '{"property":"Status","select":{"equals":"Done"}}' --json

# Full control via API
ntn api v1/data_sources/<data-source-id>/query page_size:=25
ntn api v1/data_sources/<data-source-id>/query \
  filter:='{"property":"Status","select":{"equals":"Done"}}' \
  sorts:='[{"property":"Priority","direction":"descending"}]'
```

### Create page in data source

```bash
ntn api v1/pages \
  parent[data_source_id]=<data-source-id> \
  properties[Name][title][0][text][content]="New Entry" \
  properties[Status][select][name]=Todo
```

### Deprecated (broken since Sept 2025)

```bash
# ❌ DO NOT USE — returns invalid_request_url
ntn api v1/databases/<db-id>/query
```

## Blocks

### Append blocks to page
```bash
ntn api v1/blocks/<page-id>/children -X PATCH -d '{
  "children": [
    {"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Notes"}}]}},
    {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"Some text here."}}]}}
  ]
}'
```

> ⚠️ **ntn sends POST by default when `-d` is present.** Notion's API requires `PATCH` to append blocks. Always use `-X PATCH` for this endpoint.

### Delete block
```bash
ntn api v1/blocks/<block-id> -X DELETE
```

## Pages helper (Markdown → Notion)

```bash
ntn pages create --file notes.md                    # Create from markdown file
ntn pages create --file notes.md --parent-id abc123  # Create under specific page
```

## Files

### Upload local file
```bash
ntn files create < photo.png                        # Upload via stdin
ntn files create --filename photo.png < photo.png   # Explicit filename
ntn files create --external-url https://example.com/img.png
ntn files list
```

### Upload and attach as image block (direct Notion hosting)

Upload images directly to Notion's infrastructure — no external hosting needed:

```bash
# 1. Upload image, get upload ID
UPLOAD_ID=$(ntn files create --plain < ./photo.png | cut -f1)

# 2. Attach as image block to page (must be within 1 hour of upload)
ntn api "v1/blocks/$PAGE_ID/children" -X PATCH \
  children[0][type]=image \
  children[0][image][type]=file_upload \
  children[0][image][file_upload][id]="$UPLOAD_ID"
```

**Important**:
- Upload expires after **1 hour** — attach to a page quickly
- Files up to **20MB** work with direct single-step upload
- Use `--filename` and `--content-type` if auto-detection fails
- The `--plain` flag returns TSV: `id  filename  status  mime  size  created  expiry`

### Full example: batch upload images

```bash
for img in ./assets/*.jpg; do
  echo "Uploading $img..."
  UPLOAD_ID=$(ntn files create --plain --filename "$(basename "$img")" < "$img" | cut -f1)
  ntn api "v1/blocks/$PAGE_ID/children" -X PATCH \
    children[0][type]=image \
    children[0][image][type]=file_upload \
    children[0][image][file_upload][id]="$UPLOAD_ID"
  sleep 0.5
done
```

## Comments (if needed)

```bash
ntn api v1/comments -d '{"parent":{"page_id":"abc123"},"rich_text":[{"text":{"content":"Note"}}]}'
ntn api v1/comments -d '{"parent":{"block_id":"block123"},"rich_text":[{"text":{"content":"Note"}}]}'
ntn api v1/comments -d '{"discussion_id":"disc123","rich_text":[{"text":{"content":"Reply"}}]}'
```

## Troubleshooting

```bash
ntn doctor                    # Check auth, config, latest version
ntn -v api v1/users           # Verbose mode with full error chains
ntn logout && ntn login       # Re-authenticate
```

### "Invalid request URL" when appending blocks
ntn defaults to `POST` when `-d` is passed, but Notion's `blocks/{id}/children` endpoint requires `PATCH` to append. Always use `-X PATCH`:
```bash
ntn api v1/blocks/<block-id>/children -X PATCH -d '{"children":[...]}'
```

### "Unauthorized" / expired token
The legacy token at `~/.config/notion/api_key` may be expired or revoked. Use `ntn doctor` to verify which token ntn is actually using, then re-auth via `ntn logout && ntn login`.

## Notes

- Inline databases may have different IDs than parent pages. Use `search` to find the actual DB ID.
- Piped JSON input yields raw API responses (pipe to `jq` for formatting).
- `ntn api` auto-selects HTTP method: GET by default, POST when body data present, PATCH/DELETE via `-X`.
- Workspace name: "Notion Workspace"
- Known IDs: (lokal in `~/.config/notion/ids` hinterlegt)
- Legacy `notion-cli` (github.com/4ier/notion-cli) is kept as fallback but `ntn` is preferred.

## Shell completions

```bash
ntn completions bash >> ~/.bashrc
ntn completions zsh  >> ~/.zshrc
ntn completions fish >> ~/.config/fish/config.fish
```
