#!/usr/bin/env python3
"""Append markdown content as Notion blocks to a page."""
import sys, json, re, os

PAGE_ID = sys.argv[1] if len(sys.argv) > 1 else ""
TOKEN = os.environ.get("NOTION_API_TOKEN", "")

# Read markdown file
md_path = os.path.expanduser("~/.openclaw/workspace/sources/twitter/2026-06-16_0xJeff_hermes-analyst-10x-better.md")
with open(md_path) as f:
    content = f.read()

# Strip frontmatter
content = re.sub(r'^---\n.*?---\n', '', content, flags=re.DOTALL)

blocks = []
lines = content.strip().split('\n')
i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue

    # Image
    m = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
    if m:
        alt, src = m.groups()
        blocks.append({
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": f"[Image: {alt}] — see local archive"}}]}
        })
        i += 1
        continue

    # Heading 1
    if line.startswith('# ') and not line.startswith('## '):
        blocks.append({
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}
        })
        i += 1
        continue

    # Heading 2
    if line.startswith('## '):
        blocks.append({
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}
        })
        i += 1
        continue

    # Heading 3
    if line.startswith('### '):
        blocks.append({
            "type": "heading_3",
            "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}
        })
        i += 1
        continue

    # Divider
    if line == '---':
        blocks.append({"type": "divider", "divider": {}})
        i += 1
        continue

    # Quote / blockquote
    if line.startswith('> '):
        q_text = line[2:]
        # Collect multi-line quotes
        j = i + 1
        while j < len(lines) and lines[j].strip().startswith('> '):
            q_text += '\n' + lines[j].strip()[2:]
            j += 1
        blocks.append({
            "type": "quote",
            "quote": {"rich_text": [{"type": "text", "text": {"content": q_text}}]}
        })
        i = j
        continue

    # Bullet list
    if line.startswith('- ') or line.startswith('* '):
        item_text = line[2:]
        # Notion uses single bullet blocks
        blocks.append({
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": item_text}}]}
        })
        i += 1
        continue

    # Regular paragraph
    # Parse bold markdown **text**
    rich_text = []
    parts = re.split(r'(\*\*.*?\*\*)', line)
    for part in parts:
        if part.startswith('**') and part.endswith('**'):
            rich_text.append({
                "type": "text",
                "text": {"content": part[2:-2]},
                "annotations": {"bold": True}
            })
        else:
            rich_text.append({"type": "text", "text": {"content": part}})

    blocks.append({
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text}
    })
    i += 1

# Notion API batches max 100 blocks at a time
# Use ntn CLI to append
import subprocess

batch_size = 90
for start in range(0, len(blocks), batch_size):
    batch = blocks[start:start+batch_size]
    payload = json.dumps({"children": batch})
    result = subprocess.run(
        ["ntn", "api", "v1", "blocks", PAGE_ID, "children"],
        input=payload,
        capture_output=True,
        text=True,
        env={**os.environ, "NOTION_API_TOKEN": TOKEN}
    )
    if result.returncode != 0:
        print("STDERR:", result.stderr, file=sys.stderr)
        sys.exit(1)
    print(result.stdout)

print(f"Appended {len(blocks)} blocks to Notion page {PAGE_ID}")
