#!/usr/bin/env python3
"""Upload local images to catbox.moe and replace URLs in markdown files.

Usage: python3 upload_images.py <assets_dir> [<md_dir>]
"""
import json
import re
import subprocess
import time
from pathlib import Path

URL_MAP_FILE = Path(".url_map.json")

def upload_to_catbox(filepath):
    """Upload a file to catbox.moe and return the public URL."""
    result = subprocess.run(
        ["curl", "-s", "-F", "reqtype=fileupload", "-F", f"fileToUpload=@{filepath}",
         "https://catbox.moe/user/api.php"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return url if url.startswith("https://") else None

def process_images(assets_dir, md_dir=None):
    """Upload images and update markdown files."""
    assets_dir = Path(assets_dir)
    md_dir = Path(md_dir) if md_dir else assets_dir.parent
    
    # Load existing URL map
    url_map_file = md_dir / URL_MAP_FILE
    url_map = json.loads(url_map_file.read_text()) if url_map_file.exists() else {}
    
    images = sorted(assets_dir.glob("*.jpg"))
    print(f"Found {len(images)} images to upload")
    
    for i, img_path in enumerate(images, 1):
        name = img_path.name
        if name in url_map:
            print(f"  [{i}/{len(images)}] {name} already uploaded")
            continue
        
        print(f"  [{i}/{len(images)}] Uploading {name}...")
        url = upload_to_catbox(img_path)
        if url:
            url_map[name] = url
            url_map_file.write_text(json.dumps(url_map, indent=2))
            print(f"    -> {url}")
        else:
            print(f"    FAILED")
        time.sleep(1.5)
    
    # Update markdown files
    print("\nUpdating markdown files...")
    for md_file in md_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        original = content
        
        def replace_img(match):
            alt, path = match.group(1), match.group(2)
            filename = Path(path).name
            return f"![{alt}]({url_map.get(filename, path)})" if filename in url_map else match.group(0)
        
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, content)
        if content != original:
            md_file.write_text(content, encoding="utf-8")
            print(f"  Updated: {md_file.name}")
    
    print("\nDone!")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 upload_images.py <assets_dir> [<md_dir>]")
        sys.exit(1)
    
    assets_dir = sys.argv[1]
    md_dir = sys.argv[2] if len(sys.argv) > 2 else None
    process_images(assets_dir, md_dir)

if __name__ == "__main__":
    main()
