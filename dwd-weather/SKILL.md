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
```bash
# 10-day forecast for a station
python3 dwd_weather.py forecast 10865

# With custom hourly window
python3 dwd_weather.py forecast G005 --hourly 24
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
# Search stations by name
python3 dwd_weather.py stations search Karlsruhe

# Find nearest station to coordinates
python3 dwd_weather.py stations nearest --lat 49.0373 --lon 8.3637

# Get station details
python3 dwd_weather.py stations get 10865

# Refresh station cache
python3 dwd_weather.py stations refresh
```

## Known Working Stations

| ID | Location |
|---|---|
| 10865 | Berlin-Tegel |
| G005 | Berlin |

> ⚠️ **Note:** Not all DWD climate stations work with the WarnWetter app API. The API uses MOSMIX grid points, which have different IDs than the climate stations. Use the `stations` commands to find nearby stations, then test with `forecast` to verify compatibility.

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
pytest -m "not network"

# Integration tests (requires network)
pytest -m network
```
