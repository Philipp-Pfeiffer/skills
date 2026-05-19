---
name: dwd-weather
description: "German weather forecasts and warnings via DWD (bund.dev) API. Provides 10-day forecasts, hourly data, and severe weather warnings for Germany. No API key needed."
metadata:
  {
    "openclaw":
      {
        "emoji": "🌤️",
        "requires": { "bins": ["python3"], "python": ["requests"] },
      },
  }
---

# DWD Weather Skill

Get weather forecasts and warnings for Germany via the Deutscher Wetterdienst (DWD) API, surfaced through bund.dev.

## When to Use

✅ **USE when:**
- "What's the weather in Germany?"
- "Will it rain this weekend in Karlsruhe?"
- "Any weather warnings?"
- "Temperature forecast for Berlin"

❌ **DON'T use when:**
- Locations outside Germany → use wttr.in/Open-Meteo
- Historical weather data → use wetterdienst library directly

## Commands

### Forecast

You can pass a **city name** or a **station ID**:

```bash
# By city name — auto-resolved to nearest MOSMIX station
python3 dwd_weather.py forecast Karlsruhe
python3 dwd_weather.py forecast "Beiertheim"
python3 dwd_weather.py forecast Buxtehude

# By station ID directly
python3 dwd_weather.py forecast 10865
python3 dwd_weather.py forecast G005

# With custom hourly window
python3 dwd_weather.py forecast Karlsruhe --hourly 24
```

### Warnings

```bash
# All current warnings
python3 dwd_weather.py warnings

# Specific warning types
python3 dwd_weather.py warnings --type gemeinde   # municipal
python3 dwd_weather.py warnings --type nowcast    # short-term
python3 dwd_weather.py warnings --type coast      # coastal
```

### Station Lookup

```bash
# Search MOSMIX stations by name
python3 dwd_weather.py stations search Karlsruhe

# Resolve any location to the nearest MOSMIX station
python3 dwd_weather.py stations resolve Beiertheim

# Find nearest station to coordinates
python3 dwd_weather.py stations nearest --lat 49.0373 --lon 8.3637

# Get station details by ID
python3 dwd_weather.py stations get 10865
```

## How Location Resolution Works

The skill uses a three-tier lookup:

1. **Direct station ID** — if the input looks like a MOSMIX ID (2–8 alphanumeric chars), it's used directly.
2. **Name search** — fuzzy matching against all ~6000 MOSMIX stations (handles umlauts: Köln → KOELN).
3. **Geocoding fallback** — uses Nominatim (OpenStreetMap) to get coordinates, then finds the nearest MOSMIX station.

All ~6000 MOSMIX stations are bundled in `mosmix_stations.json` (extracted from the official DWD KMZ).

## API Endpoints

- **Forecast:** `https://app-prod-ws.warnwetter.de/v30/stationOverviewExtended?stationIds=ID`
- **Warnings:** `https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16/`

## Data Units

All values from the API are in 0.1 units:
- Temperature: 0.1°C (100 = 10.0°C)
- Precipitation: 0.1 mm/h or 0.1 mm/day
- Humidity: 0.1%
- Pressure: 0.1 hPa
- Wind: 0.1 km/h

## Installation

```bash
pip install -r requirements.txt
```

## Testing

```bash
# Unit tests (no network)
python3 tests/test_dwd_weather.py

# Integration tests (requires network)
python3 -c "import pytest; pytest.main(['-m', 'network', 'tests/test_dwd_weather.py'])"
```
