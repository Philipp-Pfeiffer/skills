---
name: autobahn
description: >
  Query German highway (Autobahn) traffic data via the official Autobahn API.
  Retrieve roadworks, traffic warnings, closures, webcams, parking, and
  electric charging stations for any German road. Use when the user asks
  about traffic conditions, stau, construction, road closures, highway
  webcams, rest stops, or EV charging stations on German Autobahnen.
metadata:
  openclaw:
    emoji: "🛣️"
    requires:
      bins: ["python3"]
      python: ["requests"]
---

# Autobahn

Query current conditions on German highways via the official Autobahn API
(https://autobahn.api.bund.dev). No API key required.

## Quick Start

```bash
python3 scripts/autobahn.py --roads              # List all available roads
python3 scripts/autobahn.py A8                   # Default: roadworks + warnings
python3 scripts/autobahn.py A8 --all             # Everything
python3 scripts/autobahn.py A8 --warnings        # Traffic warnings only
python3 scripts/autobahn.py A8 --charging        # EV charging stations
```

## Available Data

| Flag | Data |
|------|------|
| `--roadworks` | Construction sites with lane restrictions and dates |
| `--warnings` | Live traffic warnings with delay minutes |
| `--closures` | Road closures (exits, bridges, etc.) |
| `--webcams` | Traffic cameras with image URLs |
| `--parking` | Rest stops with amenities |
| `--charging` | EV fast charging stations with plug types and kW |
| `--all` | All of the above |

## Common Queries

### Check traffic on a route

```bash
python3 scripts/autobahn.py A8 --warnings
```

Shows warnings like:
```
[WARNING] A8 | Pforzheim-West - Pforzheim | Karlsruhe -> Stuttgart | +13 min
```

### Find roadworks

```bash
python3 scripts/autobahn.py A8 --roadworks
```

### Find EV charging stations

```bash
python3 scripts/autobahn.py A8 --charging
```

Shows stations with plug type and power:
```
[STRONG_ELECTRIC_CHARGING_STATION] A8 | Ulm | Raststätte Sindelfinger Wald Süd (4) | Schnellladeeinrichtung
```

### Get details for a specific item

Use the identifier from list output:

```bash
python3 scripts/autobahn.py --detail warning <identifier>
python3 scripts/autobahn.py --detail roadworks <identifier>
python3 scripts/autobahn.py --detail electric_charging_station <identifier>
```

### Download a webcam image

```bash
python3 scripts/autobahn.py --download-image <imageurl> --output-dir ./images
```

## JSON Output

Add `--json` to any command for raw JSON output.

## API Notes

- Road IDs are uppercase (A8, A1, B2, etc.)
- Webcam availability varies by road and time
- Data source is the official Autobahn GmbH
- Rate limits are not documented; be reasonable

## Reference

See [references/api-details.md](references/api-details.md) for complete field documentation.
