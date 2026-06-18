#!/usr/bin/env python3
"""Upload images directly to Notion and append as image blocks to a page.

Usage: python3 upload_images_notion.py <page_id> <assets_dir>

Requires: ntn CLI authenticated
"""
import subprocess
import sys
import time
from pathlib import Path

def run_ntn(args, input_data=None):
    """Run ntn CLI and return stdout."""
    result = subprocess.run(
        ["ntn"] + args,
        capture_output=True, text=True,
        input=input_data,
        env={**__import__('os').environ,
             "PATH": "/home/linuxbrew/.linuxbrew/bin:/home/p-pfeiffer/.local/bin:" +
                     __import__('os').environ.get("PATH", "")}
    )
    if result.returncode != 0:
        print(f"  ntn error: {result.stderr.strip()}")
        return None
    return result.stdout.strip()

def upload_image(filepath):
    """Upload image to Notion and return upload ID."""
    # Read file bytes
    data = Path(filepath).read_bytes()
    
    # Upload with --plain to get TSV output: id  filename  status  mime  size  created  expiry
    output = run_ntn([
        "files", "create", "--plain",
        "--filename", filepath.name,
        "--content-type", "image/jpeg"
    ], input_data=data)
    
    if not output:
        return None
    
    # Parse TSV: first field is upload ID
    upload_id = output.split('\t')[0]
    return upload_id

def append_image_block(page_id, upload_id):
    """Append image block with file_upload to page."""
    result = run_ntn([
        "api", f"v1/blocks/{page_id}/children",
        "-X", "PATCH",
        f"children[0][type]=image",
        f"children[0][image][type]=file_upload",
        f"children[0][image][file_upload][id]={upload_id}"
    ])
    return result is not None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 upload_images_notion.py <page_id> <assets_dir>")
        sys.exit(1)
    
    page_id = sys.argv[1]
    assets_dir = Path(sys.argv[2])
    
    images = sorted(assets_dir.glob("image_*.jpg"))
    print(f"Uploading {len(images)} images to Notion page {page_id}...")
    
    for i, img_path in enumerate(images, 1):
        print(f"  [{i}/{len(images)}] {img_path.name}...", end=" ")
        
        upload_id = upload_image(img_path)
        if not upload_id:
            print("UPLOAD FAILED")
            continue
        
        success = append_image_block(page_id, upload_id)
        if success:
            print(f"OK (id: {upload_id[:20]}...)")
        else:
            print("BLOCK FAILED")
        
        time.sleep(0.5)  # Rate limiting
    
    print("\nDone!")

if __name__ == "__main__":
    main()
