---
name: notion-cli
slug: notion-cli
version: 1.0.0
description: "Notion operations via notion-cli (github.com/4ier/notion-cli). Use when (1) searching pages/databases, (2) querying or creating database entries, (3) reading or writing page content, (4) appending blocks, (5) managing comments. Requires NOTION_API_KEY env or authenticated notion-cli."
metadata: {"clawdbot":{"emoji":"📝","requires":{"env":["NOTION_API_KEY"]},"os":["linux","darwin","win32"]}}
---

# notion-cli

Binary: `notion-cli` at `~/.local/bin/notion-cli` (ensure `PATH` includes it).
Auth token: `~/.config/notion/api_key`.

## Pre-flight

Always prepend `export PATH="$HOME/.local/bin:$PATH"` or source it once. If auth fails, re-login:

```bash
notion-cli auth login --with-token <<< "$(cat ~/.config/notion/api_key)"
```

## Key Commands

**Search:** `notion-cli search "<query>"`

**View page:** `notion-cli page view <id>` (accepts full notion.so URLs)

**Query database:** `notion-cli db query <id> [--filter 'Status=Done'] [--limit 10]`

**Create page in DB:** `notion-cli page create <db-id> --db "Name=Value" "Status=Todo"`

**List blocks as Markdown:** `notion-cli block list <page-id> --depth 3 --md`

**Append blocks from file:** `notion-cli block append <page-id> --file notes.md`

**Properties:** `notion-cli page props <page-id>` / `notion-cli page props <page-id> "Status=Done"`

## Notes

- Inline databases may have different IDs than parent pages. Use `search` to find the actual DB ID.
- Property types are auto-detected from schema — no manual type hints needed.
- Piped output yields JSON (for `jq`); terminal output is formatted tables.
- Workspace name: "Notion von P. Pfeiffer"
- Known IDs: Agent Seite `2fe7ba0f-6b14-8003-b2cc-cd8d8cce9f57`, Rezepte DB `7cc390d8-ad42-4943-a9a1-35b7dda02d9d`
