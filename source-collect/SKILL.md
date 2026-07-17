---
name: source-collect
description: "Collect and archive articles, Twitter/X posts, threads, and web sources into both Notion Reference Library and local markdown sources. Use when: (1) the user sends a URL and wants it saved/extracted, (2) the user says 'save this', 'collect this', 'archive this article/post/thread', (3) importing Twitter/X content into Notion Reference Library, (4) creating local source backups with YAML frontmatter. Supports browser-based extraction for full content capture that Notion AI cannot do on its own."
---

# Source Collect

Archive URLs into Notion Reference Library + local markdown sources.

## Required Skills

This skill depends on **notion-cli** (`~/.openclaw/skills/notion-cli/SKILL.md`). Read it before performing any Notion operations. All Notion API calls must use the `ntn` CLI or the documented curl patterns from that skill.

## Workflow

1. **Extract** — Use `browser` or `web_fetch` to capture full article/post content
2. **Parse** — Extract title, author, core insight, tags/topics
3. **Local** — Save as markdown to `~/.openclaw/workspace/sources/<type>/`
4. **Notion** — Create database entry via `ntn` CLI **AND populate the page body with the full article text and images at the correct positions**

## Image Handling Rule

When archiving sources with images (Twitter/X posts, articles with screenshots, diagrams, etc.):

- **ALWAYS extract the original image URLs** from the source (e.g., via FxTwitter JSON, `media_entities`, `original_img_url`)
- **NEVER** insert placeholder text like "[Image] — see local archive" or "[Image: description]"
- Embed images as actual `image` blocks with `external` URLs pointing to the original source
- Images must be placed at the **correct position** in the text flow (where they appeared in the original article)
- If original URLs expire: upload local copies via `ntn files create` and attach as `file_upload` blocks

This is non-negotiable. Placeholder text for images is a bug, not a feature.

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
- **Local markdown:** frontmatter + optional summary + full original text
- **Notion:** The page body MUST contain the full original text as block content (paragraphs, headings, images). The database properties alone are NOT sufficient.

**Critical:** Notion entries are database rows with page content. Creating only the database row (properties) without filling the page body is incomplete. Always append the article text and images as children blocks after creating the page. **Images must be embedded as actual image blocks at their original positions, never as placeholder text.**

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