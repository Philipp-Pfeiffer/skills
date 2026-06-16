---
name: x-to-markdown
description: Convert X (Twitter) posts and long-form X Articles to Markdown, including text, headings, lists, code blocks, cover images, and inline media. Uses the free FxTwitter API and requires no API key or login.
---

# X to Markdown

Convert X (Twitter) posts and long-form **X Articles** to clean Markdown.

- No X API key or login required.
- Extracts full article text with headings, lists, code blocks, bold/italic, and links.
- Embeds cover images and inline images as Markdown image tags.
- Optionally downloads all images to a local `images/` folder.
- Works with `x.com`, `twitter.com`, `fixupx.com`, and `fxtwitter.com` URLs.

## Quick Start

Convert a post or article and print Markdown to stdout:

```bash
python scripts/x_to_markdown.py "https://x.com/akshay_pachaar/status/2064051835636498924"
```

Save to a file:

```bash
python scripts/x_to_markdown.py "https://x.com/akshay_pachaar/status/2064051835636498924" -o article.md
```

Download images next to the markdown file:

```bash
python scripts/x_to_markdown.py "https://x.com/akshay_pachaar/status/2064051835636498924" -o article.md --download-media
```

Get the raw FxTwitter JSON for custom processing:

```bash
python scripts/x_to_markdown.py "https://x.com/akshay_pachaar/status/2064051835636498924" --json
```

## Supported URLs

| URL form | Example |
|----------|---------|
| Status URL | `https://x.com/<user>/status/<id>` |
| Status URL (twitter.com) | `https://twitter.com/<user>/status/<id>` |
| FxTwitter URL | `https://fxtwitter.com/<user>/status/<id>` |

Article-only URLs (`https://x.com/i/article/<id>`) are **not** supported directly, because FxTwitter needs the parent status. Use the post URL that links to the article (usually the one containing `https://t.co/…`).

## How It Works

1. The script extracts `username` and `status_id` from the URL.
2. It calls `https://api.fxtwitter.com/<username>/status/<id>`.
3. FxTwitter returns structured JSON including the article content, cover image, and inline media.
4. The script converts Draft.js-style blocks into Markdown.

## Output Format

Articles include YAML front matter:

```markdown
---
title: "Your Agent Harness Should Repair Itself"
author: "Akshay 🚀 (@akshay_pachaar)"
url: "https://x.com/akshay_pachaar/status/2064051835636498924"
published: "Mon Jun 08 18:28:00 +0000 2026"
source: "X (Twitter)"
---

![Your Agent Harness Should Repair Itself](images/image_000.jpg)

# Your Agent Harness Should Repair Itself

…
```

## CLI Reference

```text
usage: x_to_markdown.py [-h] [-o OUTPUT] [--download-media] [--json] url

positional arguments:
  url                   X/Twitter URL (status or article link)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output markdown file (default: stdout)
  --download-media      Download images next to the output file
  --json                Print raw FxTwitter JSON instead of Markdown
```

## Notes & Limitations

- FxTwitter is a free public service. Heavy use may be rate-limited; add delays between requests if you batch-process many URLs.
- Video URLs are included as links, not embedded players.
- Article-only URLs (`x.com/i/article/...`) must be resolved to the parent post URL manually.

## Files

- `scripts/x_to_markdown.py` – main converter script
- `requirements.txt` – dependency notes (stdlib only)
