#!/usr/bin/env python3
"""Split merged markdown into separate files by PDF separators.

Usage: python3 split_md.py <input.md> <output_dir>
"""
import re
import sys
from pathlib import Path

def split_markdown(input_path, output_dir):
    """Split markdown file by separator lines."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    content = Path(input_path).read_text(encoding="utf-8")
    
    # Flexible pattern for various separator formats
    # Matches: ## === START: filename.pdf ===  or  ## START: filename.pdf  etc.
    pattern = r'(?:^|\n)#*\s*(?:=|\$)*\s*START:\s*([^\n]+?)(?:\s*(?:=|\$|:|\n))'
    
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    
    if not matches:
        print("No separators found. Copying as single file.")
        out_file = output_dir / Path(input_path).name
        out_file.write_text(content, encoding="utf-8")
        return [out_file]
    
    created = []
    
    # Preamble before first separator
    if matches[0].start() > 0:
        preamble = content[:matches[0].start()].strip()
        if preamble:
            preamble_file = output_dir / "00-preamble.md"
            preamble_file.write_text(preamble + "\n", encoding="utf-8")
            created.append(preamble_file)
    
    # Each section
    for i, match in enumerate(matches):
        filename = match.group(1).strip()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        section = content[match.start():end]
        
        # Clean filename for filesystem
        clean = filename.replace(".pdf", "").replace(".pdi", "").replace(" ", "-").replace(",", "-").replace("/", "-")
        out_file = output_dir / f"{clean}.md"
        
        # Remove separator line, keep body
        lines = section.split('\n')
        body = '\n'.join(lines[1:]).strip()
        output = f"# {filename}\n\n{body}\n"
        
        out_file.write_text(output, encoding="utf-8")
        created.append(out_file)
        print(f"Created: {out_file.name}")
    
    print(f"\nSplit into {len(created)} files in {output_dir}")
    return created

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 split_md.py <input.md> <output_dir>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_dir = sys.argv[2]
    split_markdown(input_path, output_dir)

if __name__ == "__main__":
    main()
