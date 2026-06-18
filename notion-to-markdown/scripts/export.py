#!/usr/bin/env python3
"""Export a Notion page to Markdown with images and all block types.

Usage: python3 export.py <page_id> <output_dir>

Handles: headings, paragraphs, lists, code, images, tables, toggles,
callouts, quotes, dividers, equations, rich text formatting.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

class NotionExporter:
    def __init__(self, page_id, output_dir):
        self.page_id = page_id
        self.output_dir = Path(output_dir)
        self.assets_dir = self.output_dir / "assets"
        self.image_counter = 1
        self.downloaded = {}  # url -> local_path cache
    
    def ntn(self, args):
        """Run ntn CLI and return parsed JSON."""
        env = {**os.environ, "PATH": os.path.expanduser("~/.local/bin") + ":" + os.environ.get("PATH", "")}
        result = subprocess.run(["ntn"] + args, capture_output=True, text=True, env=env)
        if result.returncode != 0:
            print(f"ntn error: {result.stderr}", file=sys.stderr)
            return None
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return None
    
    def fetch_blocks(self, block_id):
        """Fetch all blocks recursively with pagination."""
        blocks = []
        cursor = None
        while True:
            args = ["api", f"v1/blocks/{block_id}/children"]
            if cursor:
                args.append(f"start_cursor=={cursor}")
            resp = self.ntn(args)
            if not resp:
                break
            for block in resp.get("results", []):
                blocks.append(block)
                # Fetch children recursively
                if block.get("has_children"):
                    block["children"] = self.fetch_blocks(block["id"])
            if not resp.get("has_more"):
                break
            cursor = resp.get("next_cursor")
        return blocks
    
    def get_page_title(self):
        """Get page title."""
        resp = self.ntn(["api", f"v1/pages/{self.page_id}"])
        if resp:
            try:
                return resp["properties"]["title"]["title"][0]["text"]["content"]
            except (KeyError, IndexError):
                pass
        return "Untitled"
    
    def download_image(self, url):
        """Download image from Notion to local assets dir."""
        if url in self.downloaded:
            return self.downloaded[url]
        
        ext = ".jpg"
        if ".png" in url.lower():
            ext = ".png"
        elif ".gif" in url.lower():
            ext = ".gif"
        elif ".webp" in url.lower():
            ext = ".webp"
        
        filename = f"image_{self.image_counter:03d}{ext}"
        filepath = self.assets_dir / filename
        
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                with open(filepath, "wb") as f:
                    f.write(resp.read())
            self.downloaded[url] = f"assets/{filename}"
            self.image_counter += 1
            return self.downloaded[url]
        except Exception as e:
            print(f"  failed to download image: {e}", file=sys.stderr)
            return None
    
    def rich_text_to_md(self, rich_text):
        """Convert Notion rich_text array to Markdown string."""
        parts = []
        for rt in rich_text:
            text = rt.get("plain_text", "")
            if not text:
                continue
            
            ann = rt.get("annotations", {})
            
            # Inline equation
            if rt.get("type") == "equation":
                expr = rt.get("equation", {}).get("expression", "")
                parts.append(f"${expr}$")
                continue
            
            # Mentions
            if rt.get("type") == "mention":
                mention = rt.get("mention", {})
                if mention.get("type") == "page":
                    page_id = mention.get("page", {}).get("id", "")
                    parts.append(f"[@{text}](https://www.notion.so/{page_id.replace('-', '')})")
                else:
                    parts.append(text)
                continue
            
            # Links
            href = rt.get("href")
            if href:
                text = f"[{text}]({href})"
            
            # Formatting
            if ann.get("code"):
                text = f"`{text}`"
            if ann.get("bold"):
                text = f"**{text}**"
            if ann.get("italic"):
                text = f"*{text}*"
            if ann.get("strikethrough"):
                text = f"~~{text}~~"
            if ann.get("underline"):
                text = f"<u>{text}</u>"
            
            # Color (skip default)
            color = ann.get("color", "default")
            if color != "default":
                text = f"<span style=\"color:{color}\">{text}</span>"
            
            parts.append(text)
        
        return "".join(parts)
    
    def block_to_md(self, block, indent=0):
        """Convert a Notion block (and its children) to Markdown."""
        bt = block.get("type", "")
        prefix = "  " * indent
        md = ""
        
        # Helper to get rich_text content
        def get_text(field):
            return self.rich_text_to_md(block.get(bt, {}).get("rich_text", []))
        
        if bt == "paragraph":
            text = get_text("paragraph")
            if text.strip():
                md += f"{prefix}{text}\n\n"
            else:
                md += "\n"
        
        elif bt == "heading_1":
            text = get_text("heading_1")
            md += f"{prefix}# {text}\n\n"
        
        elif bt == "heading_2":
            text = get_text("heading_2")
            md += f"{prefix}## {text}\n\n"
        
        elif bt == "heading_3":
            text = get_text("heading_3")
            md += f"{prefix}### {text}\n\n"
        
        elif bt == "bulleted_list_item":
            text = get_text("bulleted_list_item")
            md += f"{prefix}- {text}\n"
        
        elif bt == "numbered_list_item":
            text = get_text("numbered_list_item")
            md += f"{prefix}1. {text}\n"
        
        elif bt == "to_do":
            text = get_text("to_do")
            checked = block.get("to_do", {}).get("checked", False)
            box = "[x]" if checked else "[ ]"
            md += f"{prefix}- {box} {text}\n"
        
        elif bt == "code":
            code_data = block.get("code", {})
            lang = code_data.get("language", "")
            text = self.rich_text_to_md(code_data.get("rich_text", []))
            md += f"{prefix}```{lang}\n{text}\n```\n\n"
        
        elif bt == "quote":
            text = get_text("quote")
            lines = text.split('\n')
            for line in lines:
                md += f"{prefix}> {line}\n"
            md += "\n"
        
        elif bt == "callout":
            text = get_text("callout")
            icon = block.get("callout", {}).get("icon", {})
            emoji = icon.get("emoji", "💡") if icon.get("type") == "emoji" else "💡"
            md += f"{prefix}> **{emoji} {text}**\n\n"
        
        elif bt == "divider":
            md += f"{prefix}---\n\n"
        
        elif bt == "image":
            img = block.get("image", {})
            url = None
            caption = ""
            
            if img.get("type") == "file":
                url = img.get("file", {}).get("url")
            elif img.get("type") == "external":
                url = img.get("external", {}).get("url")
            
            # Caption
            cap_rich = img.get("caption", [])
            if cap_rich:
                caption = self.rich_text_to_md(cap_rich)
            
            if url:
                local_path = self.download_image(url)
                if local_path:
                    md += f"{prefix}![{caption}]({local_path})\n\n"
                else:
                    md += f"{prefix}<!-- image: {url} -->\n\n"
            else:
                md += f"{prefix}<!-- image without URL -->\n\n"
        
        elif bt == "file":
            file_data = block.get("file", {})
            name = file_data.get("name", "file")
            url = file_data.get("external", {}).get("url") if file_data.get("type") == "external" else file_data.get("file", {}).get("url")
            if url:
                md += f"{prefix}[📎 {name}]({url})\n\n"
            else:
                md += f"{prefix}<!-- file: {name} -->\n\n"
        
        elif bt == "pdf":
            pdf_data = block.get("pdf", {})
            name = pdf_data.get("name", "PDF")
            url = pdf_data.get("external", {}).get("url") if pdf_data.get("type") == "external" else pdf_data.get("file", {}).get("url")
            if url:
                md += f"{prefix}[📄 {name}]({url})\n\n"
            else:
                md += f"{prefix}<!-- pdf: {name} -->\n\n"
        
        elif bt == "video":
            vid = block.get("video", {})
            url = vid.get("external", {}).get("url") if vid.get("type") == "external" else vid.get("file", {}).get("url")
            if url:
                md += f"{prefix}[🎬 Video]({url})\n\n"
            else:
                md += f"{prefix}<!-- video -->\n\n"
        
        elif bt == "bookmark":
            bk = block.get("bookmark", {})
            url = bk.get("url", "")
            caption = self.rich_text_to_md(bk.get("caption", []))
            md += f"{prefix}[🔗 {caption or url}]({url})\n\n"
        
        elif bt == "embed":
            emb = block.get("embed", {})
            url = emb.get("url", "")
            md += f"{prefix}[🌐 Embed]({url})\n\n"
        
        elif bt == "equation":
            expr = block.get("equation", {}).get("expression", "")
            md += f"{prefix}$${expr}$$\n\n"
        
        elif bt == "table":
            md += f"{prefix}<!-- table -->\n\n"
        
        elif bt == "table_row":
            cells = block.get("table_row", {}).get("cells", [])
            row = " | ".join(self.rich_text_to_md(cell) for cell in cells)
            md += f"{prefix}| {row} |\n"
        
        elif bt == "toggle":
            text = get_text("toggle")
            md += f"{prefix}<details>\n{prefix}<summary>{text}</summary>\n\n"
        
        elif bt == "link_to_page":
            link = block.get("link_to_page", {})
            page_id = link.get("page_id", "")
            db_id = link.get("database_id", "")
            target = page_id or db_id
            md += f"{prefix}[→ Link to page](https://www.notion.so/{target.replace('-', '')})\n\n"
        
        elif bt == "breadcrumb" or bt == "column_list" or bt == "column":
            # Skip layout containers
            pass
        
        else:
            md += f"{prefix}<!-- block type: {bt} -->\n\n"
        
        # Process children
        children = block.get("children", [])
        for child in children:
            child_md = self.block_to_md(child, indent + 1)
            md += child_md
        
        # Close toggle
        if bt == "toggle" and children:
            md += f"{prefix}</details>\n\n"
        
        return md
    
    def export(self):
        """Run the full export."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        
        title = self.get_page_title()
        print(f"Exporting: {title}")
        
        blocks = self.fetch_blocks(self.page_id)
        print(f"  Found {len(blocks)} top-level blocks")
        
        md = f"# {title}\n\n"
        for block in blocks:
            md += self.block_to_md(block)
        
        # Clean up excessive blank lines
        md = re.sub(r'\n{3,}', '\n\n', md)
        
        out_file = self.output_dir / f"{title.replace(' ', '-').lower()}.md"
        out_file.write_text(md, encoding="utf-8")
        
        print(f"\nDone!")
        print(f"  Markdown: {out_file}")
        print(f"  Images: {self.image_counter - 1} downloaded to {self.assets_dir}")
        return out_file

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 export.py <page_id> <output_dir>")
        sys.exit(1)
    
    exporter = NotionExporter(sys.argv[1], sys.argv[2])
    exporter.export()

if __name__ == "__main__":
    main()
