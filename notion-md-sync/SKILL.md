---
name: notion-md-sync
description: Export Notion pages to Markdown with images, split into separate files by PDF separators, and re-import back to Notion. Use when the user needs to (1) export a Notion page to local Markdown, (2) split merged Notion imports into individual pages, (3) re-upload Markdown files with images back to Notion as child pages.
metadata:
  openclaw:
    emoji: "🔄"
    requires:
      bins: ["ntn", "python3"]
      python: []
      node: []
---

# Notion ↔ Markdown Sync

Bidirectional sync between Notion pages and local Markdown files with image support.

## Prerequisites

- `ntn` CLI installed and authenticated (`ntn doctor` passes)
- `python3` available

## Workflow

### 1. Export Notion Page to Markdown

```bash
python3 scripts/export_notion.py <page_id> <output_dir>
```

Creates:
- `<output_dir>/<title>.md` — Markdown file
- `<output_dir>/assets/` — downloaded images

**Important**: Notion image URLs expire after 1 hour. Export immediately.

### 2. Split Merged Markdown (Optional)

When a page contains merged PDFs with separator lines:

```bash
python3 scripts/split_md.py <input.md> <output_dir>
```

Detects separators like `## === START: filename.pdf ===` and creates one file per section.

### 3. Upload Images Directly to Notion

Upload images to Notion's own infrastructure — no external hosting needed:

```bash
# Upload image and get upload ID
UPLOAD_ID=$(ntn files create --plain < ./image.png | cut -f1)

# Attach as image block to page (must be within 1 hour)
ntn api "v1/blocks/$PAGE_ID/children" -X PATCH \
  children[0][type]=image \
  children[0][image][type]=file_upload \
  children[0][image][file_upload][id]="$UPLOAD_ID"
```

**Notes**:
- Upload expires after **1 hour** — attach quickly
- Files up to **20MB** work with direct upload
- See `scripts/upload_images_notion.py` for batch processing

### 4. Import Markdown to Notion

```bash
# Create page with markdown content via stdin
cat file.md | ntn pages create --parent page:<parent_id>
```

## Full Example

```bash
# Export
python3 scripts/export_notion.py 11e7ba0f-... ./24516-export

# Split
python3 scripts/split_md.py ./24516-export/*.md ./24516-export/split/

# Images are handled directly via ntn files create when re-importing
# Upload each image, note the upload ID, then attach as block

# Import
for f in ./24516-export/split/*.md; do
  cat "$f" | ntn pages create --parent page:11e7ba0f-...
done
```

## Scripts

- `scripts/export_notion.py` — Export page to Markdown with images
- `scripts/split_md.py` — Split merged file by separators
- For image upload: use `ntn files create` directly (no external hosting needed)
- For import: use `ntn pages create` with stdin
