---
name: fbi-wanted
description: >
  Query the FBI Wanted public API to retrieve information about wanted persons,
  fugitives, and missing persons. Use when the user asks about FBI most wanted,
  wanted persons, fugitives, missing persons, FBI alerts, or wants to search
  the FBI wanted database by name, category, field office, or reward amount.
metadata:
  openclaw:
    emoji: "🕵️"
    requires:
      bins: ["python3"]
      python: ["requests"]
---

# FBI Wanted

Query the FBI Wanted public API (https://api.fbi.gov/wanted/v1/list). No API key required.

## Quick Start

Run the bundled script:

```bash
python3 scripts/fbi_wanted.py --list
python3 scripts/fbi_wanted.py --top
python3 scripts/fbi_wanted.py --search "Bob Tang"
python3 scripts/fbi_wanted.py --details <uid>
```

## Common Operations

### List wanted persons

First page:
```bash
python3 scripts/fbi_wanted.py --list
```

All pages (slow, ~60 requests for full dataset):
```bash
python3 scripts/fbi_wanted.py --list --all
```

### Filter by category

Server-side filter. Common subjects:
- `Violent Crime - Murders`
- `Kidnappings and Missing Persons`
- `White-Collar Crime`
- `Counterintelligence`
- `Seeking Information`
- `Criminal Enterprise Investigations`
- `Ten Most Wanted Fugitives`

```bash
python3 scripts/fbi_wanted.py --list --category "Violent Crime - Murders"
```

### Filter by FBI field office

Server-side filter. Examples: `newark`, `sanfrancisco`, `washingtondc`, `miami`.

```bash
python3 scripts/fbi_wanted.py --list --office newark
```

### Search by name

Client-side search across all pages:

```bash
python3 scripts/fbi_wanted.py --search "Bob Tang"
```

### Top Ten Most Wanted

Shortcut for `--category "Ten Most Wanted Fugitives" --all`:

```bash
python3 scripts/fbi_wanted.py --top
```

### Filter by minimum reward

Client-side filter:

```bash
python3 scripts/fbi_wanted.py --all --reward-min 10000
```

### Show details for a specific person

```bash
python3 scripts/fbi_wanted.py --details <uid>
```

### Download an image

```bash
python3 scripts/fbi_wanted.py --download-image <url> --output-dir ./images
```

## JSON Output

Add `--json` to any command to get raw JSON instead of formatted text:

```bash
python3 scripts/fbi_wanted.py --list --json
```

## Combining Filters

Filters can be combined. Order of application:
1. Server-side: `field_offices`, `subjects` (category)
2. Client-side: `--search`, `--reward-min`, `--status`
3. Finally: `--limit`

Example:
```bash
python3 scripts/fbi_wanted.py --all --office newark --reward-min 5000 --limit 5
```

## API Notes

- Pagination: 20 items per page
- Total count returned in `total` field
- Server-side filters: `field_offices`, `subjects`
- All other filtering is client-side and requires fetching all pages
- Images and PDFs are hosted on fbi.gov (external URLs)
- Rate limits are not documented; use reasonable request pacing

## Reference

For a complete list of field offices and subjects, see [references/api-details.md](references/api-details.md).
