---
name: notion-to-markdown
description: Export Notion pages to Markdown accurately, preserving formatting, images, tables, equations, nested blocks, and all rich text. Use when the user needs to (1) export a Notion page to local Markdown, (2) download images from Notion, (3) convert Notion's block structure to Markdown, (4) backup Notion content as version-controlled Markdown.
metadata:
  openclaw:
    emoji: "📤"
    requires:
      bins: ["ntn", "python3"]
      python: []
      node: []
---

# Notion → Markdown Export

Accurate bidirectional export from Notion to Markdown with full block-type coverage.

## What This Skill Covers

- **Complete block type support**: headings, paragraphs, lists, code, images, tables, toggles, callouts, quotes, equations, bookmarks, embeds, files, videos
- **Rich text formatting**: bold, italic, code, strikethrough, underline, colors, links, mentions, inline equations
- **Image download**: Notion's temporary image URLs are fetched immediately before expiry
- **Nested blocks**: toggles, columns, and child pages are handled recursively
- **Table rendering**: table_rows converted to Markdown pipe tables

## Why Not Just `ntn pages get`?

`ntn pages get <page-id>` returns a simplified Markdown representation but:
- Images are referenced as Notion URLs (expire after 1 hour)
- Tables may be rendered as HTML or omitted
- Nested blocks (toggles, columns) are flattened
- Block-level equations may be lost
- File attachments are not downloaded

This skill provides **accurate, complete** export with local assets.

## Prerequisites

```bash
ntn doctor                    # Verify auth and setup
python3 --version             # Python 3.8+
```

## Quick Start

```bash
python3 scripts/export.py <page_id> <output_dir>
```

Creates:
- `<output_dir>/<page-title>.md` — the Markdown file
- `<output_dir>/assets/` — downloaded images with sequential naming

## Supported Block Types

| Notion Block | Markdown Output |
|---|---|
| `paragraph` | Plain text paragraph |
| `heading_1/2/3` | `#` / `##` / `###` |
| `bulleted_list_item` | `- item` |
| `numbered_list_item` | `1. item` |
| `to_do` | `- [ ] item` / `- [x] item` |
| `code` | ```lang\ncode\n``` |
| `quote` | `> quoted text` |
| `callout` | `> **💡 text**` |
| `divider` | `---` |
| `image` | `![caption](assets/image_001.jpg)` |
| `file` / `pdf` | `[📎 filename](url)` |
| `bookmark` / `embed` | `[🔗 text](url)` |
| `equation` (block) | `$$expr$$` |
| `table` + `table_row` | `| col1 | col2 |` pipe table |
| `toggle` | `<details><summary>text</summary>…</details>` |
| `link_to_page` | `[→ Link](notion-url)` |
| `mention` (page) | `[@Name](notion-url)` |

## Rich Text Formatting

| Notion Annotation | Markdown |
|---|---|
| Bold | `**text**` |
| Italic | `*text*` |
| Code | `` `text` `` |
| Strikethrough | `~~text~~` |
| Underline | `<u>text</u>` |
| Link | `[text](url)` |
| Inline equation | `$expr$` |
| Colored text | `<span style="color:red">text</span>` |

## Critical: Image URLs Expire

Notion's image block URLs (both `file` and `external` type) include an `expiry_time` — typically **1 hour** from fetch. The export script downloads all images immediately during the block traversal.

**Do not delay** between fetching blocks and downloading images. If you fetch blocks, wait 2 hours, then try to download — the URLs will be dead.

## The Export Script

`scripts/export.py` is a self-contained Python script that:

1. Fetches the page title via `ntn api v1/pages/{id}`
2. Recursively fetches all blocks via `ntn api v1/blocks/{id}/children` with pagination
3. Downloads images to `assets/` with sequential naming
4. Converts each block to Markdown with proper nesting
5. Writes the final `.md` file

### Pagination

Notion returns max 100 blocks per request. The script follows `has_more` / `next_cursor` automatically.

### Block Nesting

Notion blocks can have children (`has_children: true`). The script fetches children recursively and indents them appropriately (toggles get `<details>`, nested lists get indentation).

### Tables

Notion tables are blocks with `table_row` children. Each cell contains rich_text. The script produces:

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

Note: Notion does not expose table header information via API — all rows render as data rows. You may need to manually bold the first row.

## Example: Export a Database of Lecture Notes

```bash
# 1. Search for the database
ntn api v1/search -d '{"query":"Lecture Notes"}' | jq '.results[0].id'

# 2. Query all pages in the database
ntn api v1/databases/DB_ID/query page_size:=100 | jq '.results[].id'

# 3. Export each page
for page_id in $(cat page_ids.txt); do
  python3 scripts/export.py "$page_id" "./lectures/$page_id"
done
```

## Limitations

- **Table headers**: Notion API does not distinguish header rows; first row is not auto-bolded
- **Column layouts**: `column_list` / `column` blocks render as flat Markdown (columns are linearized)
- **Database views**: Inline databases are referenced as links, not exported as tables
- **Comments**: Not exported (Notion API limitation)
- **Page history**: Not exported (Notion API limitation)

## Troubleshooting

### "Image download failed"

The image URL expired. Re-run the export — blocks and images must be fetched in the same session.

### "ntn error: Unauthorized"

Run `ntn doctor` and re-authenticate if needed.

### Missing blocks

If a block type is not listed above, the script outputs `<!-- block type: TYPE -->` as a placeholder. Open an issue with the block type.

## Related

- `notion-md-sync` — bidirectional sync (export → split → re-import)
- `notion-cli` — lower-level ntn API operations
