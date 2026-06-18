#!/usr/bin/env python3
"""
source-collect: Extrahiert Artikel/Posts und legt sie in Notion + lokale Sources ab.

Usage:
  python3 collect.py <url> [--title "..."] [--author "..."] [--type article|twitter|thread]

Beispiel:
  python3 collect.py "https://x.com/garrytan/status/..." --title "Skillify" --author "@garrytan" --type twitter
"""

import sys
import os
import re
import json
import argparse
import subprocess
import datetime
from urllib.parse import urlparse
from pathlib import Path

# Konfiguration
SOURCES_DIR = os.path.expanduser("~/.openclaw/workspace/sources")
NOTION_API_TOKEN = os.environ.get("NOTION_API_TOKEN", "")
NOTION_DB_ID = "04f32113-9015-4884-8325-7b6c1e29c0d2"
NTN_BIN = os.path.expanduser("~/.local/bin/ntn")

def run_cmd(cmd, input_data=None):
    """Führt Shell-Kommando aus und gibt stdout zurück."""
    env = os.environ.copy()
    env["NOTION_API_TOKEN"] = NOTION_API_TOKEN
    env["PATH"] = os.path.expanduser("~/.local/bin") + ":" + env.get("PATH", "")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env, input=input_data)
    if result.returncode != 0 and result.stderr:
        print(f"[WARN] Command stderr: {result.stderr[:200]}", file=sys.stderr)
    return result.stdout.strip(), result.returncode

def slugify(text):
    """Erzeugt einen Datei-sicheren Slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text[:60].strip('-')

def fetch_content(url):
    """Holt Content via curl + simple HTML extraction."""
    import urllib.request
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8', errors='replace')
    except Exception as e:
        # Fallback: try curl
        stdout, rc = run_cmd(f'curl -sL --max-time 30 -A "Mozilla/5.0" "{url}"')
        if rc != 0:
            return {"title": "", "text": "", "html": ""}
        html = stdout

    # Extract title
    title_match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.I)
    title = title_match.group(1).strip() if title_match else ""

    # Remove scripts/styles
    html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S|re.I)
    html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.S|re.I)

    # Extract paragraphs (simple)
    paras = re.findall(r'<p[^>]*>([^<]+)</p>', html_clean, re.I)
    text = "\n\n".join(p.strip() for p in paras if len(p.strip()) > 30)

    return {"title": title, "text": text[:8000], "html": html[:2000]}

def determine_source_type(url):
    """Bestimmt den Source-Typ aus der URL."""
    domain = urlparse(url).netloc.lower()
    if any(d in domain for d in ["x.com", "twitter.com", "t.co"]):
        return "twitter"
    elif "reddit.com" in domain or "reddit" in domain:
        return "thread"
    else:
        return "article"

def determine_author(url, title="", author_hint=""):
    """Extrahiert den Author aus URL oder Hinweis."""
    if author_hint:
        return author_hint
    # Twitter: @handle aus URL
    match = re.search(r'(?:x\.com|twitter\.com)/([^/?]+)', url)
    if match:
        return f"@{match.group(1)}"
    return ""

def generate_filename(url, title, author, source_type, date_str):
    """Generiert Dateinamen im lokalen Format: YYYY-MM-DD_author_slug.md"""
    date = date_str or datetime.date.today().isoformat()
    author_slug = slugify(author) if author else "unknown"
    title_slug = slugify(title) if title else "untitled"
    # Limit: YYYY-MM-DD_author_first-few-words.md
    short_title = '-'.join(title_slug.split('-')[:4])
    return f"{date}_{author_slug}_{short_title}.md"

def create_local_file(url, title, author, source_type, content, tags=None):
    """Erstellt die lokale Markdown-Datei im richtigen Unterordner."""
    date_str = datetime.date.today().isoformat()
    folder = os.path.join(SOURCES_DIR, source_type)
    os.makedirs(folder, exist_ok=True)
    
    filename = generate_filename(url, title, author, source_type, date_str)
    filepath = os.path.join(folder, filename)
    
    # YAML Frontmatter
    tags_list = tags or []
    if isinstance(tags_list, str):
        tags_list = [t.strip() for t in tags_list.split(",")]
    
    frontmatter = f"""---
source: {url}
author: "{author}"
date: {date_str}
tags: {json.dumps(tags_list)}
status: unread
---

# {title or "Untitled"}

## Kernpunkte

- 

## Warum relevant



---

## Original-Text

{content.get('text', '') or '(Content konnte nicht extrahiert werden)'}
"""
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(frontmatter)
    
    return filepath

def create_notion_entry(url, title, author, source_type, core_insight="", domains=None, topics=None, quality="TBD"):
    """Erstellt Eintrag in Notion Reference Library Database."""
    if not NOTION_API_TOKEN:
        print("[ERROR] NOTION_API_TOKEN not set", file=sys.stderr)
        return None
    
    # Map source_type to Type field
    type_map = {"twitter": "Tweet / Thread", "thread": "Thread / Discussion", "article": "Article"}
    notion_type = type_map.get(source_type, "Article")
    
    # Build properties payload
    props = {
        "Title": {"title": [{"text": {"content": title or "Untitled"}}]},
        "URL": {"url": url},
        "Author/Source": {"rich_text": [{"text": {"content": author or ""}}]},
        "Type": {"select": {"name": notion_type}},
        "Status": {"select": {"name": "Unread"}},
        "Quality": {"select": {"name": quality}},
    }
    
    if core_insight:
        props["Core Insight"] = {"rich_text": [{"text": {"content": core_insight[:2000]}}]}
    
    if domains:
        if isinstance(domains, str):
            domains = [d.strip() for d in domains.split(",")]
        props["Domains"] = {"multi_select": [{"name": d} for d in domains if d]}
    
    if topics:
        if isinstance(topics, str):
            topics = [t.strip() for t in topics.split(",")]
        props["Topics"] = {"multi_select": [{"name": t} for t in topics if t]}
    
    # Use ntn CLI
    cmd = f'{NTN_BIN} api v1/pages -d \'{json.dumps({"parent": {"data_source_id": NOTION_DB_ID}, "properties": props})}\''
    stdout, rc = run_cmd(cmd)
    
    if rc != 0:
        print(f"[ERROR] Notion create failed: {stdout}", file=sys.stderr)
        return None
    
    try:
        result = json.loads(stdout)
        return result.get("id")
    except (json.JSONDecodeError, KeyError):
        return stdout

def main():
    parser = argparse.ArgumentParser(description="Collect source into Notion + local archive")
    parser.add_argument("url", help="URL to collect")
    parser.add_argument("--title", default="", help="Override title")
    parser.add_argument("--author", default="", help="Override author")
    parser.add_argument("--type", choices=["twitter", "article", "thread"], help="Override source type")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--domains", default="", help="Comma-separated domains for Notion")
    parser.add_argument("--topics", default="", help="Comma-separated topics for Notion")
    parser.add_argument("--insight", default="", help="Core insight summary")
    parser.add_argument("--quality", default="TBD", help="Quality rating")
    args = parser.parse_args()
    
    # Determine type
    source_type = args.type or determine_source_type(args.url)
    
    # Fetch content
    print(f"[1/3] Fetching content from {args.url}...")
    content = fetch_content(args.url)
    
    # Determine metadata
    title = args.title or content.get("title", "")
    author = determine_author(args.url, title, args.author)
    
    print(f"[2/3] Creating local file ({source_type})...")
    local_path = create_local_file(args.url, title, author, source_type, content, args.tags)
    print(f"      → {local_path}")
    
    print(f"[3/3] Creating Notion entry...")
    notion_id = create_notion_entry(
        args.url, title, author, source_type,
        core_insight=args.insight,
        domains=args.domains,
        topics=args.topics,
        quality=args.quality
    )
    if notion_id:
        print(f"      → Notion page ID: {notion_id}")
    else:
        print(f"      → Notion entry creation failed (check token)")
    
    print(f"\n✓ Collected: {title or 'Untitled'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
