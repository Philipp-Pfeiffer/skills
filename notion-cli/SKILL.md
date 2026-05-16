---
name: notion-cli
slug: notion-cli
version: 2.0.0
description: "Notion operations via the official Notion CLI (ntn). Use when (1) searching pages/databases, (2) querying or creating database entries, (3) reading or writing page content, (4) appending blocks, (5) managing comments, (6) deploying Notion Workers. Authenticated via keychain or NOTION_API_TOKEN."
metadata: {"clawdbot":{"emoji":"📝","requires":{"env":["NOTION_API_TOKEN"]},"os":["linux","darwin","win32"]}}
---

# notion-cli

Binary: `ntn` at `~/.local/bin/ntn` (ensure `PATH` includes it).  
Auth: `ntn login` (browser flow, keychain) or `NOTION_API_TOKEN` env var.

## Pre-flight

```bash
export PATH="$HOME/.local/bin:$PATH"
ntn doctor          # Verify setup
```

If auth fails and you have a legacy token at `~/.config/notion/api_key`:

```bash
NOTION_API_TOKEN="$(cat ~/.config/notion/api_key)" ntn api v1/users
```

## Key Commands

### Search
```bash
ntn api v1/search -d '{"query":"<query>"}'
```

### Read page
```bash
ntn api v1/pages/<page-id>
```

### Query database
```bash
ntn api v1/databases/<db-id>/query -d '{"page_size":10}'
```

### Create page in DB
```bash
ntn api v1/pages -d '{
  "parent": {"database_id":"<db-id>"},
  "properties": {
    "Name": {"title":[{"text":{"content":"New Entry"}}]},
    "Status": {"select":{"name":"Todo"}}
  }
}'
```

### List blocks (page children)
```bash
ntn api v1/blocks/<page-id>/children
```

### Update page properties
```bash
ntn api v1/pages/<page-id> -X PATCH -d '{"properties":{"Status":{"select":{"name":"Done"}}}}'
```

### Inline body syntax (no JSON quoting)
```bash
ntn api v1/pages parent[page_id]=abc123 properties[Name][title][0][text][content]=Hello
ntn api v1/pages/abc123 -X PATCH archived:=true
```

## Pages helper (Markdown → Notion)
```bash
ntn pages create --file notes.md
```

## Files
```bash
ntn files create < photo.png
ntn files list
```

## Notes

- Inline databases may have different IDs than parent pages. Use `search` to find the actual DB ID.
- Piped JSON input yields raw API responses (pipe to `jq` for formatting).
- Workspace name: "Notion von P. Pfeiffer"
- Known IDs: Agent Seite `2fe7ba0f-6b14-8003-b2cc-cd8d8cce9f57`, Rezepte DB `7cc390d8-ad42-4943-a9a1-35b7dda02d9d`
- Legacy `notion-cli` (github.com/4ier/notion-cli) is kept as fallback but `ntn` is preferred.
