import os
import json
import math
import csv
import io
import urllib.request
from urllib.parse import urlencode
from datetime import datetime, timezone

CACHE_DIR = os.path.expanduser("~/.cache/dwd-weather")
STATIONS_FILE = os.path.join(CACHE_DIR, "stations.json")
STATIONS_URL = "https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/recent/KL_Tageswerte_Beschreibung_Stationen.txt"

# Known working WarnWetter app stations
KNOWN_WORKING_STATIONS = {
    "10865": {"name": "Berlin-Tegel", "lat": 52.5597, "lon": 13.2877},
    "G005": {"name": "Berlin", "lat": 52.5, "lon": 13.4},
    # Karlsruhe area — need to discover working ones
}

def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)

def parse_stations(raw: bytes) -> list[dict]:
    """Parse the DWD stations list (ISO-8859-1 encoded, fixed-width or space-separated)."""
    text = raw.decode('iso-8859-1', errors='replace')
    lines = text.strip().split('\n')
    stations = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('Stations_id'):
            continue
        parts = line.split()
        if len(parts) < 7:
            continue
        try:
            # Format: ID begin_date end_date height lat lon name state type
            # The name may contain spaces, so we parse from the end
            # IDs are numeric, dates are YYYYMMDD
            station_id = parts[0]
            begin = parts[1]
            end = parts[2]
            height = float(parts[3])
            lat = float(parts[4])
            lon = float(parts[5])
            # Everything from index 6 to before the last 2 is the name
            # Last 2 are typically state and type
            name_parts = parts[6:-2] if len(parts) > 8 else parts[6:]
            name = ' '.join(name_parts)
            state = parts[-2] if len(parts) > 7 else ''
            stations.append({
                "id": station_id,
                "name": name,
                "lat": lat,
                "lon": lon,
                "height": height,
                "state": state,
                "begin": begin,
                "end": end,
            })
        except (ValueError, IndexError):
            continue
    return stations

def fetch_stations(force=False) -> list[dict]:
    """Fetch and cache the DWD stations list."""
    ensure_cache_dir()
    if not force and os.path.exists(STATIONS_FILE):
        with open(STATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    req = urllib.request.Request(STATIONS_URL, headers={"User-Agent": "dwd-weather-skill/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
    
    stations = parse_stations(raw)
    with open(STATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)
    return stations

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance in km between two lat/lon points."""
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_nearest_station(lat: float, lon: float, stations: list[dict] = None) -> dict:
    """Find the nearest DWD station to given coordinates."""
    if stations is None:
        stations = fetch_stations()
    if not stations:
        return None
    
    nearest = min(stations, key=lambda s: haversine(lat, lon, s["lat"], s["lon"]))
    distance = haversine(lat, lon, nearest["lat"], nearest["lon"])
    nearest["distance_km"] = round(distance, 1)
    return nearest

def search_stations(query: str, stations: list[dict] = None) -> list[dict]:
    """Fuzzy search stations by name."""
    if stations is None:
        stations = fetch_stations()
    query = query.lower()
    results = []
    for s in stations:
        if query in s["name"].lower() or query in s["state"].lower():
            results.append(s)
    return results

def get_station_by_id(station_id: str, stations: list[dict] = None) -> dict:
    """Get station by ID."""
    if stations is None:
        stations = fetch_stations()
    for s in stations:
        if s["id"] == station_id:
            return s
    return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: stations.py <search|nearest|get> ...")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) >= 3:
        q = sys.argv[2]
        results = search_stations(q)
        for r in results[:10]:
            print(f"{r['id']:8s} {r['name']:30s} {r['lat']:8.4f} {r['lon']:8.4f} {r['state']}")
    elif cmd == "nearest" and len(sys.argv) >= 4:
        lat, lon = float(sys.argv[2]), float(sys.argv[3])
        s = find_nearest_station(lat, lon)
        if s:
            print(f"Nearest: {s['id']} {s['name']} ({s['distance_km']} km)")
        else:
            print("No stations found")
    elif cmd == "get" and len(sys.argv) >= 3:
        s = get_station_by_id(sys.argv[2])
        if s:
            print(json.dumps(s, indent=2, ensure_ascii=False))
        else:
            print("Station not found")
    else:
        print("Usage: stations.py <search QUERY|nearest LAT LON|get ID>")
