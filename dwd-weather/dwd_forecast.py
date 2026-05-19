import json
import gzip
import urllib.request
from datetime import datetime, timezone

API_BASE = "https://app-prod-ws.warnwetter.de/v30"
WARNINGS_BASE = "https://s3.eu-central-1.amazonaws.com/app-prod-static.warnwetter.de/v16"

# DWD uses these sentinel values for "no data"
SENTINEL_VALUES = {32767, -32768, -32767, -999}


def _clean_value(value, divisor=10):
    """Convert raw API value to usable float, treating sentinels as None."""
    if value is None:
        return None
    if value in SENTINEL_VALUES:
        return None
    return value / divisor


def _clean_int(value):
    """Convert raw API int value, treating sentinels as None."""
    if value is None:
        return None
    if value in SENTINEL_VALUES:
        return None
    return value


import gzip

def _fetch_json(url: str, timeout: int = 30) -> dict:
    """Fetch JSON from a URL with error handling and gzip support."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "dwd-weather-skill/1.0",
        "Accept-Encoding": "gzip",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            # Check if response is gzip compressed
            if raw[:2] == b'\x1f\x8b':
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

def get_forecast(station_id: str) -> dict:
    """Fetch 10-day forecast for a station."""
    url = f"{API_BASE}/stationOverviewExtended?stationIds={station_id}"
    data = _fetch_json(url)
    
    if "error" in data:
        return data
    
    if not data or station_id not in data:
        return {"error": f"Station {station_id} not found or no data available."}
    
    station = data[station_id]
    f1 = station.get("forecast1", {})
    days = station.get("days", [])
    
    # Parse hourly data
    start_ms = f1.get("start", 0)
    time_step = f1.get("timeStep", 3600000)  # ms
    start_dt = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)
    
    hourly = []
    temps = f1.get("temperature", [])
    rain = f1.get("precipitationTotal", [])
    hum = f1.get("humidity", [])
    dew = f1.get("dewPoint2m", [])
    pressure = f1.get("surfacePressure", [])
    icons = f1.get("icon", [])
    
    for i in range(len(temps)):
        entry = {
            "hour": i,
            "datetime": (start_dt.replace(tzinfo=None) if i == 0 else None),
            "temperature_c": _clean_value(temps[i]) if i < len(temps) else None,
            "rain_mm_h": _clean_value(rain[i]) if i < len(rain) else None,
            "humidity_pct": _clean_value(hum[i]) if i < len(hum) else None,
            "dewpoint_c": _clean_value(dew[i]) if i < len(dew) else None,
            "pressure_hpa": _clean_value(pressure[i]) if i < len(pressure) else None,
            "icon": _clean_int(icons[i]) if i < len(icons) else None,
        }
        hourly.append(entry)
    
    # Parse daily data
    daily = []
    for day in days:
        daily.append({
            "date": day.get("dayDate"),
            "temp_max_c": _clean_value(day.get("temperatureMax", 0)),
            "temp_min_c": _clean_value(day.get("temperatureMin", 0)),
            "precipitation_mm": _clean_value(day.get("precipitation", 0)),
            "sunshine_min": _clean_value(day.get("sunshine", 0)),
            "wind_speed_kmh": _clean_value(day.get("windSpeed")),
            "wind_gust_kmh": _clean_value(day.get("windGust")),
            "wind_direction": _clean_int(day.get("windDirection")),
            "icon": _clean_int(day.get("icon")),
        })
    
    return {
        "station_id": station_id,
        "forecast_start": start_dt.isoformat(),
        "hourly": hourly,
        "daily": daily,
    }

def get_warnings(warning_type: str = "gemeinde") -> dict:
    """Fetch current weather warnings."""
    endpoints = {
        "gemeinde": f"{WARNINGS_BASE}/gemeinde_warnings_v2.json",
        "nowcast": f"{WARNINGS_BASE}/warnings_nowcast.json",
        "coast": f"{WARNINGS_BASE}/warnings_coast.json",
        "all": None,
    }
    
    if warning_type == "all":
        results = {}
        for key, url in endpoints.items():
            if url:
                results[key] = _fetch_json(url)
        return results
    
    url = endpoints.get(warning_type)
    if not url:
        return {"error": f"Unknown warning type: {warning_type}. Use: gemeinde, nowcast, coast, all"}
    
    return _fetch_json(url)

def format_forecast(data: dict, hourly_count: int = 12) -> str:
    """Format forecast data into a human-readable string."""
    if "error" in data:
        return f"Error: {data['error']}"
    
    lines = []
    lines.append(f"📍 Station: {data['station_id']}")
    lines.append(f"🕐 Forecast from: {data['forecast_start'][:16]}")
    lines.append("")
    
    # Daily summary
    lines.append("📅 Daily Forecast:")
    for day in data["daily"][:10]:
        date = day["date"]
        tmin = day["temp_min_c"]
        tmax = day["temp_max_c"]
        rain = day["precipitation_mm"]
        rain_str = f" | 🌧️ {rain:.1f}mm" if rain > 0 else ""
        lines.append(f"  {date}: {tmin:.1f}° – {tmax:.1f}°C{rain_str}")
    
    lines.append("")
    lines.append(f"⏰ Next {hourly_count} Hours:")
    for h in data["hourly"][:hourly_count]:
        temp = h["temperature_c"]
        rain = h["rain_mm_h"]
        hum = h["humidity_pct"]
        if temp is not None:
            rain_str = f" | 🌧️ {rain:.1f}mm/h" if rain and rain > 0 else ""
            lines.append(f"  +{h['hour']:2d}h: {temp:5.1f}°C | 💧 {hum:.0f}%{rain_str}")
        else:
            lines.append(f"  +{h['hour']:2d}h: —")
    
    return "\n".join(lines)

def format_warnings(data: dict, warning_type: str) -> str:
    """Format warnings into human-readable string."""
    if "error" in data:
        return f"Error: {data['error']}"
    
    lines = []
    lines.append(f"⚠️ Warnings ({warning_type}):")
    
    if warning_type == "all":
        for wtype, wdata in data.items():
            lines.append(f"\n  {wtype.upper()}:")
            lines.append(format_warnings(wdata, wtype))
        return "\n".join(lines)
    
    # Parse different warning formats
    if "warnings" in data:
        warnings = data["warnings"]
        if isinstance(warnings, list):
            if not warnings:
                lines.append("  No active warnings.")
            for w in warnings[:5]:
                level = w.get("level", 0)
                event = w.get("event", "Unknown")
                start = w.get("start", 0)
                end = w.get("end", 0)
                start_str = datetime.fromtimestamp(start / 1000, tz=timezone.utc).strftime("%d.%m.%H:%M") if start else "?"
                end_str = datetime.fromtimestamp(end / 1000, tz=timezone.utc).strftime("%d.%m.%H:%M") if end else "?"
                level_str = ["", "Minor", "Moderate", "Severe", "Extreme"][min(level, 4)]
                lines.append(f"  [{level_str}] {event} ({start_str} – {end_str})")
                if w.get("descriptionText"):
                    desc = w["descriptionText"][:100] + "..." if len(w["descriptionText"]) > 100 else w["descriptionText"]
                    lines.append(f"    {desc}")
        elif isinstance(warnings, dict):
            for region_id, region_warnings in warnings.items():
                if isinstance(region_warnings, list):
                    for w in region_warnings[:3]:
                        event = w.get("event", "Unknown")
                        level = w.get("level", 0)
                        lines.append(f"  [{level}] {event} (Region: {region_id})")
    else:
        lines.append(f"  Raw data keys: {list(data.keys())[:5]}")
    
    return "\n".join(lines)
