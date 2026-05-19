---
name: pdf-maker
description: Convert text, Markdown, or HTML to PDF documents. Use when the user asks to create a PDF, export something as PDF, convert markdown/HTML to PDF, or format a document for printing/sharing. Supports multiple backends (weasyprint, wkhtmltopdf, pandoc) with automatic fallback. Handles basic styling, code formatting, and table rendering.
---

# PDF Maker

## Overview

Convert text, Markdown, or HTML into styled PDF documents. Auto-detects available tools on the system and picks the best backend.

## Workflow

### Step 1: Check available backends

Run `~/.openclaw/workspace/skills/pdf-maker/scripts/check_backends.py` to see what's installed.

Priority order:
1. **weasyprint** — best CSS support, pure Python
2. **wkhtmltopdf** — good rendering, requires binary
3. **pandoc** — versatile, requires LaTeX for PDF
4. **html-to-pdf fallback** — basic Python-only fallback

### Step 2: Prepare content

Convert user content to HTML with inline CSS styling.

For **Markdown** → use Python `markdown` library or manual conversion.
For **HTML** → use directly.
For **plain text** → wrap in `<pre>` or basic HTML structure.

### Step 3: Generate PDF

Use the best available backend:

```bash
# WeasyPrint (preferred)
weasyprint input.html output.pdf

# wkhtmltopdf
wkhtmltopdf input.html output.pdf

# Pandoc
pandoc input.md -o output.pdf

# Python fallback
python3 ~/.openclaw/workspace/skills/pdf-maker/scripts/html_to_pdf.py input.html output.pdf
```

### Step 4: Deliver

Send PDF to user via message tool with `filePath` and `media` pointing to the generated file.

## Styling Guidelines

Default CSS for documents:
- Font: Georgia/serif for body, system sans for headings
- Line-height: 1.6
- Max-width: 800px equivalent
- Margins: 40px top/bottom, 20px sides
- Code blocks: monospace, light gray background
- Blockquotes: left border + italic
- Tables: border-collapse, alternating rows

## Error Handling

If no backend is available:
1. Attempt `pip install weasyprint` or system package install
2. If install fails, send HTML/ Markdown file instead with explanation
3. Log which backend was used for future reference

## Scripts

- `scripts/check_backends.py` — detect available PDF tools
- `scripts/html_to_pdf.py` — basic Python fallback using reportlab/fpdf if available

## References

- `references/styling.css` — default CSS template for documents
