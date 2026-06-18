#!/usr/bin/env python3
"""Export a Notion page to Markdown with images.

Usage: python3 export_notion.py <page_id> <output_dir>
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

def run_ntn(args):
    """Run ntn CLI command and return parsed JSON."""
    env = {**os.environ, "PATH": os.path.expanduser("~/.local/bin") + ":" + os.environ.get("PATH", "")}
    result = subprocess.run(["ntn"] + args, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        print(f"ntn error: {result.stderr}", file=sys.stderr)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

def fetch_all_blocks(page_id):
    """Fetch all blocks recursively from a Notion page."""
    blocks = []
    cursor = None
    while True:
        args = ["api", f"v1/blocks/{page_id}/children"]
        if cursor:
            args.append(f"start_cursor=={cursor}")
        resp = run_ntn(args)
        if not resp:
            break
        blocks.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        cursor = resp.get("next_cursor")
    return blocks

def extract_plain_text(rich_text):
    """Extract plain text from rich_text array, preserving basic formatting."""
    parts = []
    for rt in rich_text:
        t = rt.get("plain_text", "")
        ann = rt.get("annotations", {})
        if ann.get("bold"):
            t = f"**{t}**"
        if ann.get("italic"):
            t = f"*{t}*"
        if ann.get("code"):
            t = f"`{t}`"
        if ann.get("strikethrough"):
            t = f"~~{t}~~"
        if rt.get("type") == "equation":
            expr = rt.get("equation", {}).get("expression", "")
            t = f"$${expr}$$"
        parts.append(t)
    return "".join(parts)

def block_to_md(block, assets_dir, image_counter):
    """Convert a Notion block to Markdown string."""
    bt = block.get("type", "")
    
    if bt == "paragraph":
        text = extract_plain_text(block.get("paragraph", {}).get("rich_text", []))
        return text + "\n\n", image_counter
    
    elif bt == "heading_1":
        text = extract_plain_text(block.get("heading_1", {}).get("rich_text", []))
        return f"# {text}\n\n", image_counter
    
    elif bt == "heading_2":
        text = extract_plain_text(block.get("heading_2", {}).get("rich_text", []))
        return f"## {text}\n\n", image_counter
    
    elif bt == "heading_3":
        text = extract_plain_text(block.get("heading_3", {}).get("rich_text", []))
        return f"### {text}\n\n", image_counter
    
    elif bt == "bulleted_list_item":
        text = extract_plain_text(block.get("bulleted_list_item", {}).get("rich_text", []))
        return f"- {text}\n", image_counter
    
    elif bt == "numbered_list_item":
        text = extract_plain_text(block.get("numbered_list_item", {}).get("rich_text", []))
        return f"1. {text}\n", image_counter
    
    elif bt == "code":
        code = block.get("code", {})
        lang = code.get("language", "")
        text = extract_plain_text(code.get("rich_text", []))
        return f"```{lang}\n{text}\n```\n\n", image_counter
    
    elif bt == "image":
        img = block.get("image", {})
        url = None
        if img.get("type") == "file":
            url = img.get("file", {}).get("url")
        elif img.get("type") == "external":
            url = img.get("external", {}).get("url")
        
        if url:
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            elif ".gif" in url.lower():
                ext = ".gif"
            filename = f"image_{image_counter:03d}{ext}"
            filepath = assets_dir / filename
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as response:
                    with open(filepath, "wb") as f:
                        f.write(response.read())
                print(f"  downloaded {filename}")
                return f"![{filename}](assets/{filename})\n\n", image_counter + 1
            except Exception as e:
                print(f"  failed to download image: {e}", file=sys.stderr)
                return f"<!-- image download failed: {url} -->\n\n", image_counter + 1
        return "\n", image_counter
    
    elif bt == "child_page":
        title = block.get("child_page", {}).get("title", "")
        return f"<!-- child page: {title} -->\n\n", image_counter
    
    else:
        return f"<!-- block type: {bt} -->\n", image_counter

def page_to_markdown(page_id, output_dir):
    """Export a Notion page to Markdown with images."""
    output_dir = Path(output_dir)
    assets_dir = output_dir / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Get page title
    page = run_ntn(["api", f"v1/pages/{page_id}"])
    if not page:
        print("Failed to fetch page info", file=sys.stderr)
        return None
    
    title = "Untitled"
    try:
        title = page["properties"]["title"]["title"][0]["text"]["content"]
    except (KeyError, IndexError):
        pass
    
    # Fetch all blocks
    print(f"Fetching blocks for '{title}'...")
    blocks = fetch_all_blocks(page_id)
    print(f"  Found {len(blocks)} blocks")
    
    # Convert to markdown
    md = f"# {title}\n\n"
    image_counter = 1
    for block in blocks:
        block_md, image_counter = block_to_md(block, assets_dir, image_counter)
        md += block_md
    
    out_file = output_dir / f"{title.replace(' ', '-').lower()}.md"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"\nDone! Markdown: {out_file}")
    print(f"Images: {image_counter - 1} downloaded to {assets_dir}")
    return out_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 export_notion.py <page_id> <output_dir>")
        sys.exit(1)
    
    page_id = sys.argv[1]
    output_dir = sys.argv[2]
    page_to_markdown(page_id, output_dir)

if __name__ == "__main__":
    main()
