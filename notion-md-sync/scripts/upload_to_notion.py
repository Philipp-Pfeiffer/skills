#!/usr/bin/env python3
"""Upload markdown files to Notion as child pages.

Usage: python3 upload_to_notion.py <parent_page_id> <md_dir>
"""
import subprocess
import sys
import time
from pathlib import Path

def run_ntn(args):
    """Run ntn CLI command."""
    env = {**__import__('os').environ,
           "PATH": "/home/linuxbrew/.linuxbrew/bin:/home/p-pfeiffer/.local/bin:" +
                   __import__('os').environ.get("PATH", "")}
    return subprocess.run(["ntn"] + args, capture_output=True, text=True, env=env)

def upload_pages(parent_id, md_dir):
    """Upload all markdown files as Notion child pages."""
    md_dir = Path(md_dir)
    md_files = sorted(md_dir.glob("*.md"))
    
    # Skip the original merged file and preamble
    md_files = [f for f in md_files
                if f.name not in ["24516-datenbanksysteme.md", "00-preamble.md"]]
    
    print(f"Uploading {len(md_files)} pages to Notion (parent: {parent_id})...")
    
    for md_file in md_files:
        print(f"\nCreating page: {md_file.stem}")
        
        result = run_ntn(["pages", "create", "--parent", f"page:{parent_id}"])
        
        if result.returncode != 0:
            print(f"  Error: {result.stderr}")
            continue
        
        page_id = result.stdout.strip()
        print(f"  Page ID: {page_id}")
        time.sleep(1)
    
    print("\nDone!")

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 upload_to_notion.py <parent_page_id> <md_dir>")
        sys.exit(1)
    
    parent_id = sys.argv[1]
    md_dir = sys.argv[2]
    upload_pages(parent_id, md_dir)

if __name__ == "__main__":
    main()
