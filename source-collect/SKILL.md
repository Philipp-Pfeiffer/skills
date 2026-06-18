---
name: source-collect
description: "Collect and archive articles, Twitter/X posts, threads, and web sources into both Notion Reference Library and local markdown sources. Use when: (1) the user sends a URL and wants it saved/extracted, (2) the user says 'save this', 'collect this', 'archive this article/post/thread', (3) importing Twitter/X content into Notion Reference Library, (4) creating local source backups with YAML frontmatter. Supports browser-based extraction for full content capture that Notion AI cannot do on its own."
---

# Source Collect

Archive URLs into Notion Reference Library + local markdown sources.

## Workflow

1. **Extract** — Use `browser` or `web_fetch` to capture full article/post content
2. **Parse** — Extract title, author, core insight, tags/topics
3. **Local** — Save as markdown to `~/.openclaw/workspace/sources/<type>/`
4. **Notion** — Create database entry via `ntn` CLI with all metadata

## Source Types

| Type | URL Pattern | Local Folder | Notion Type |
|------|------------|--------------|-------------|
| Twitter/X | `x.com`, `twitter.com` | `sources/twitter/` | Tweet / Thread |
| Article | everything else | `sources/articles/` | Article |
| Thread | `reddit.com` | `sources/threads/` | Thread / Discussion |

## Deep Dive: Follow Links & Threads

When a source contains links to related material (papers, articles, threads), **follow them** and archive those too.

- Twitter/X posts with links → archive the post AND the linked resource
- Threads with multiple posts → check if it's a thread; if so, consider the thread continuation
- Mark cross-references in frontmatter: `links_to:` and `linked_from:`
- If the linked resource is substantial (paper, article), create a separate entry

This is not optional busywork — it's how you build a connected knowledge graph instead of isolated snippets.

## Rule: Always Include Full Original Text

When archiving sources, the **complete original text** must always be preserved in full.

- A brief summary or "Kernpunkte" section at the top is acceptable and useful
- But the full, unabridged original text must follow — no truncation, no "see original" placeholders
- Local markdown: frontmatter + optional summary + full original text
- Notion: optional summary blocks + full original text as page content

If extraction fails, mark as "needs extraction" rather than storing a summary alone.

## Local File Format

Naming: `YYYY-MM-DD_author_slug-keywords.md`

Structure:
```markdown
---
source: <url>
author: "@handle or Name"
date: YYYY-MM-DD
tags: [tag1, tag2]
status: unread
---

<full original text here — no summaries, no analysis>
```

Old template with "Kernpunkte" / "Warum relevant" / "Original-Text" sections is **deprecated**.

## Notion Entry Fields

See `references/notion-schema.md` for complete schema.

Key mappings:
- `Title` → extracted or provided title
- `URL` → source URL
- `Author/Source` → @handle or author name
- `Type` → mapped from source type
- `Status` → "Unread"
- `Core Insight` → 1-2 sentence summary (if available)
- `Domains` / `Topics` → extracted or provided tags
- `Quality` → "TBD" unless user specifies

## CLI Script

For automation or cron usage:
```bash
python3 ~/.openclaw/skills/source-collect/scripts/collect.py <url> \
  --title "..." --author "..." --type twitter \
  --tags "ai,agents" --domains "AI" --topics "agent-reliability" \
  --insight "Key takeaway here" --quality High
```

## Auth Requirements

- `NOTION_API_TOKEN` must be set (from `~/.config/notion/api_key`)
- `ntn` CLI must be in PATH (`~/.local/bin/ntn`)

## Handling Failures

- If Notion fails: still save locally, report to user
- If extraction fails: save with empty body + "needs extraction" note
- If title missing: use "Untitled — <domain>"
- If author missing: infer from URL or leave blank