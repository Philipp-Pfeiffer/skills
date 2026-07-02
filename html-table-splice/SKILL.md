---
name: html-table-splice
description: >
  Reassemble a large image from an HTML table splice (tile grid) into a single
  high-resolution image. Use when a website displays a poster/image split into
  multiple <td background="..."> tiles. Handles colspan/rowspan, downloads all
  tiles, iteratively solves column widths and row heights, then merges into one
  image. Optionally hosts the result via Tailscale Serve for direct download.
metadata:
  openclaw:
    emoji: "🧩"
    requires:
      bins: [python3, curl]
      python: [Pillow]
---

# HTML Table Splice Reassembly

Reconstruct a full-resolution image from a website that splits it into an HTML
`<table>` of background-image tiles.

## When to use

- A website shows a poster / infographic as a grid of small images
- The HTML uses `<td background="images/xxx.jpg" width="..." height="...">`
- You want the original resolution, not a screenshot

## Algorithm

1. **Fetch HTML** — load the page source
2. **Parse cells** — extract all `<td>` elements with `background`, `width`, `height`,
   `colspan`, `rowspan`
3. **Place in grid** — for each row, find the first unoccupied column; account for
   `rowspan` occupancy in subsequent rows
4. **Solve dimensions** — iteratively distribute cell widths/heights across their
   spanned columns/rows until all constraints are satisfied
5. **Download tiles** — fetch all `background` image URLs (parallel with `xargs -P`)
6. **Assemble** — paste each tile at its solved `(x, y)` onto a canvas
7. **Host (optional)** — copy result to a served directory for Tailscale download

## Workflow

### Step 1: Identify the target

Find the URL with the table-spliced image. The HTML typically contains:

```html
<table width="4750" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td colspan="13" rowspan="6" background="images/Tile_01.jpg" width="468" height="90" />
    <td colspan="42" rowspan="4" background="images/Tile_02.jpg" width="1452" height="63" />
    ...
  </tr>
</table>
```

### Step 2: Run the script

```bash
python3 ~/.openclaw/skills/html-table-splice/scripts/reassemble.py \
  "https://example.com/poster/" \
  /path/to/output.jpg
```

The script:
- Auto-detects `width="4750"` from the `<table>` tag
- Downloads all tiles to `/tmp/table_splice_tiles/`
- Iterates up to 100 passes to converge column/row dimensions
- Saves the merged image

### Step 3: Verify

Check the output dimensions and file size:

```bash
identify output.jpg
```

### Step 4: Host via Tailscale (optional)

For direct download without compression:

```bash
# Copy to a served directory
cp output.jpg /path/to/served/static/poster.jpg

# Tailscale Serve must already proxy that path
# Access at: https://assistomat.tailf6708a.ts.net/mockup/static/poster.jpg
```

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Massive overlaps (>1000) | Column widths guessed wrong instead of solved | Use iterative solver, not `width // colspan` |
| Canvas 24,000+ px tall | Row heights accumulated incorrectly | Ensure rowspan cells don't duplicate height |
| Missing tiles ("Missing: N") | Filename mismatch (padding) | Verify URL pattern matches saved filenames |
| White gaps | Table width ≠ sum of column widths | Adjust `TABLE_WIDTH` to match `<table>` tag |

## Known limitations

- Requires Python 3 + Pillow (`pip install Pillow`)
- Tiles must be accessible without cookies/auth
- Does not handle JavaScript-rendered tables (static HTML only)
