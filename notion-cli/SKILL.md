---
name: notion-cli
slug: notion-cli
version: 2.1.0
description: "Notion operations via the official Notion CLI (ntn). Use when (1) searching pages/databases, (2) querying or creating database entries, (3) reading or writing page content, (4) appending blocks, (5) managing comments, (6) deploying Notion Workers, (7) uploading files. Authenticated via keychain or NOTION_API_TOKEN."
metadata: {"clawdbot":{"emoji":"📝","requires":{"env":["NOTION_API_TOKEN"]},"os":["linux","darwin","win32"]}}
---

# notion-cli

Binary: `ntn` at `~/.local/bin/ntn` (ensure `PATH` includes it).  
Auth: `ntn login` (browser flow, OS keychain) or `NOTION_API_TOKEN` env var.

## Pre-flight

```bash
export PATH="$HOME/.local/bin:$PATH"
ntn doctor                    # Verify setup and auth
ntn --version                 # Check installed version
ntn update                    # Self-update to latest
```

If auth fails and you have a legacy token at `~/.config/notion/api_key`:

```bash
NOTION_API_TOKEN="$(cat ~/.config/notion/api_key)" ntn api v1/users
```

For file-based auth instead of OS keychain:

```bash
NOTION_KEYRING=0 ntn login    # Writes ~/.config/notion/auth.json
```

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
ntn api v1/blocks/<page-id>/children -d '{"page_size":100}'
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

## Databases

### Query database
```bash
ntn api v1/databases/<db-id>/query -d '{"page_size":10}'
ntn api v1/databases/<db-id>/query -d '{"filter":{"property":"Status","select":{"equals":"Done"}}}'
```

### Get database schema
```bash
ntn api v1/databases/<db-id>
```

### Query + jq (practical filter patterns)
```bash
# List all page names from DB query
ntn api v1/databases/<db-id>/query | jq '.results[] | .properties.Name.title[0].text.content'

# Extract IDs and URLs
ntn api v1/databases/<db-id>/query | jq '.results[] | {id: .id, url: .url}'
```

## Blocks

### Append blocks to page
```bash
ntn api v1/blocks/<page-id>/children -d '{
  "children": [
    {"object":"block","type":"heading_2","heading_2":{"rich_text":[{"type":"text","text":{"content":"Notes"}}]}},
    {"object":"block","type":"paragraph","paragraph":{"rich_text":[{"type":"text","text":{"content":"Some text here."}}]}}
  ]
}'
```

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

```bash
ntn files create < photo.png                        # Upload local file
ntn files create --external-url https://example.com/img.png
ntn files list
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
ntn logout && ntn login     # Re-authenticate
```

## Notes

- Inline databases may have different IDs than parent pages. Use `search` to find the actual DB ID.
- Piped JSON input yields raw API responses (pipe to `jq` for formatting).
- `ntn api` auto-selects HTTP method: GET by default, POST when body data present, PATCH/DELETE via `-X`.
- Workspace name: "Notion von P. Pfeiffer"
- Known IDs:
  - Agent Seite: `2fe7ba0f-6b14-8003-b2cc-cd8d8cce9f57`
  - Rezepte DB: `7cc390d8-ad42-4943-a9a1-35b7dda02d9d`
- Legacy `notion-cli` (github.com/4ier/notion-cli) is kept as fallback but `ntn` is preferred.

## Shell completions

```bash
ntn completions bash >> ~/.bashrc
ntn completions zsh  >> ~/.zshrc
ntn completions fish >> ~/.config/fish/config.fish
```
