#!/usr/bin/env python3
"""Reassemble an HTML table splice into a single high-resolution image.

Usage:
    python3 reassemble.py <URL> <output.jpg>

Example:
    python3 reassemble.py "https://www.medi-learn.de/examen/BiochemiePoster/" biochemie.jpg
"""
import re, sys, os, urllib.request
from PIL import Image


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read().decode('latin-1')


def parse_table(html: str):
    """Parse all <td> cells with background images from the HTML."""
    cell_re = re.compile(
        r'<td\s+([^>]*)background\s*=\s*"images/([^"]+)"([^>]*)/>',
        re.IGNORECASE,
    )

    def parse_attrs(*parts):
        attrs = {}
        for part in parts:
            for m in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', part):
                attrs[m.group(1).lower()] = m.group(2)
        return attrs

    rows_html = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    all_cells = []
    for row_idx, row_html in enumerate(rows_html):
        for m in cell_re.finditer(row_html):
            attrs = parse_attrs(m.group(1), m.group(3))
            all_cells.append({
                'img': m.group(2),
                'w': int(attrs.get('width', 0)),
                'h': int(attrs.get('height', 0)),
                'cs': int(attrs.get('colspan', 1)),
                'rs': int(attrs.get('rowspan', 1)),
                'row': row_idx,
            })
    return all_cells


def place_cells(cells):
    """Determine column position for each cell, respecting rowspan occupancy."""
    occupied = {}
    for cell in cells:
        c = 0
        while (cell['row'], c) in occupied:
            c += 1
        cell['col'] = c
        for dr in range(cell['rs']):
            for dc in range(cell['cs']):
                occupied[(cell['row'] + dr, c + dc)] = True


def solve_dimensions(cells, table_width: int):
    """Iteratively solve column widths and row heights from cell constraints."""
    max_col = max(c['col'] + c['cs'] for c in cells)
    max_row = max(c['row'] + c['rs'] for c in cells)

    # Initial guess
    col_widths = {c: table_width / max_col for c in range(max_col)}
    row_heights = {r: 30.0 for r in range(max_row)}

    for iteration in range(200):
        max_err = 0.0

        # Column pass
        for cell in cells:
            cols = range(cell['col'], cell['col'] + cell['cs'])
            total = sum(col_widths[c] for c in cols)
            err = cell['w'] - total
            if abs(err) > 0.1 and cell['cs'] > 0:
                for c in cols:
                    col_widths[c] += err / cell['cs']
                max_err = max(max_err, abs(err))

        # Row pass
        for cell in cells:
            rows = range(cell['row'], cell['row'] + cell['rs'])
            total = sum(row_heights[r] for r in rows)
            err = cell['h'] - total
            if abs(err) > 0.1 and cell['rs'] > 0:
                for r in rows:
                    row_heights[r] += err / cell['rs']
                max_err = max(max_err, abs(err))

        if max_err < 0.1:
            print(f"Converged after {iteration + 1} iterations")
            break
    else:
        print("Warning: did not fully converge")

    return col_widths, row_heights


def download_tiles(cells, base_url: str, out_dir: str = "/tmp/table_splice_tiles"):
    """Download all tile images in parallel."""
    os.makedirs(out_dir, exist_ok=True)
    seen = set()
    urls = []
    for cell in cells:
        if cell['img'] not in seen:
            seen.add(cell['img'])
            urls.append(f"{base_url}/images/{cell['img']}")

    # Write URL list for xargs
    list_file = os.path.join(out_dir, "_urls.txt")
    with open(list_file, "w") as f:
        for url in urls:
            fname = url.split("/")[-1]
            f.write(f"{url}\t{out_dir}/{fname}\n")

    print(f"Downloading {len(urls)} tiles...")
    os.system(f"cat {list_file} | xargs -P 20 -n 2 sh -c 'curl -sL -o "$2" "$1"' _")
    return out_dir


def assemble(cells, col_widths, row_heights, tile_dir: str, output: str):
    """Paste all tiles onto a canvas and save."""
    tiles = []
    for cell in cells:
        x = int(round(sum(col_widths[c] for c in range(cell['col']))))
        y = int(round(sum(row_heights[r] for r in range(cell['row']))))
        tiles.append({
            'file': cell['img'],
            'x': x,
            'y': y,
            'w': cell['w'],
            'h': cell['h'],
        })

    max_x = max(t['x'] + t['w'] for t in tiles)
    max_y = max(t['y'] + t['h'] for t in tiles)
    print(f"Canvas: {max_x} x {max_y}")

    canvas = Image.new('RGB', (max_x, max_y), (255, 255, 255))
    placed = missing = 0
    for t in tiles:
        path = os.path.join(tile_dir, t['file'])
        if os.path.exists(path):
            img = Image.open(path)
            if img.size != (t['w'], t['h']):
                img = img.resize((t['w'], t['h']), Image.LANCZOS)
            canvas.paste(img, (t['x'], t['y']))
            placed += 1
        else:
            missing += 1

    print(f"Placed: {placed}, Missing: {missing}")
    canvas.save(output, "JPEG", quality=95)
    print(f"Saved: {output} ({os.path.getsize(output) // 1024} KB)")


def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <URL> <output.jpg>")
        sys.exit(1)

    url = sys.argv[1]
    output = sys.argv[2]
    base_url = url.rstrip("/")

    html = fetch_html(url)
    tw_match = re.search(r'<table[^>]*width="(\d+)"', html)
    table_width = int(tw_match.group(1)) if tw_match else 4750
    print(f"Table width: {table_width}")

    cells = parse_table(html)
    print(f"Cells: {len(cells)}")

    place_cells(cells)
    col_widths, row_heights = solve_dimensions(cells, table_width)

    tile_dir = download_tiles(cells, base_url)
    assemble(cells, col_widths, row_heights, tile_dir, output)


if __name__ == "__main__":
    main()
