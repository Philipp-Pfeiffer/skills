import os
import json
import math
import urllib.request
import urllib.parse

# Load MOSMIX stations bundled with the skill
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOSMIX_STATIONS_PATH = os.path.join(SCRIPT_DIR, "mosmix_stations.json")

# Persistent cache for resolved locations
CACHE_DIR = os.path.expanduser("~/.cache/dwd-weather")
STATION_CACHE_FILE = os.path.join(CACHE_DIR, "station_cache.json")

# WarnWetter API known working stations (manual overrides / confirmations)
KNOWN_WORKING_STATIONS = {
    "10865": {"name": "Berlin-Tegel", "lat": 52.5597, "lon": 13.2877},
    "G005": {"name": "Berlin-Marzahn", "lat": 52.53, "lon": 13.57},
    "10727": {"name": "Karlsruhe", "lat": 49.03, "lon": 8.37},
    "Q208": {"name": "Karlsruhe", "lat": 49.0, "lon": 8.45},
}


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _load_station_cache() -> dict:
    """Load persistent station cache."""
    if os.path.exists(STATION_CACHE_FILE):
        try:
            with open(STATION_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_station_cache(cache: dict):
    """Save persistent station cache."""
    _ensure_cache_dir()
    with open(STATION_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _cache_key(query: str) -> str:
    """Normalize a query into a cache key."""
    return _normalize(query)


def _load_stations() -> list[dict]:
    """Load MOSMIX stations from bundled JSON."""
    with open(MOSMIX_STATIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# Cache in module scope
_stations_cache = None


def get_stations() -> list[dict]:
    """Get all MOSMIX stations (cached)."""
    global _stations_cache
    if _stations_cache is None:
        _stations_cache = _load_stations()
    return _stations_cache


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


_UMLAUT_MAP = str.maketrans({
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue",
    "á": "a", "à": "a", "â": "a", "ã": "a",
    "é": "e", "è": "e", "ê": "e",
    "í": "i", "ì": "i", "î": "i",
    "ó": "o", "ò": "o", "ô": "o", "õ": "o",
    "ú": "u", "ù": "u", "û": "u",
})


def _normalize(text: str) -> str:
    """Normalize text for search: lowercase, replace umlauts, strip spaces."""
    return text.lower().translate(_UMLAUT_MAP).replace(" ", "").replace("-", "").replace("/", "")


def _score_station_match(query: str, name: str) -> int:
    """Score how well query matches station name. Higher = better."""
    q = query.lower()
    n = name.lower()
    q_norm = _normalize(query)
    n_norm = _normalize(name)

    if q == n:
        return 10000  # exact match
    if q_norm == n_norm:
        return 9500  # normalized exact match (Köln == Koeln)
    if n.startswith(q + " ") or n.startswith(q + "-") or n.startswith(q + "/"):
        return 8000  # query is prefix of first word
    # query is a whole word inside (word boundaries)
    if f" {q} " in n or f"-{q}-" in n or f" {q}-" in n or f"-{q} " in n or f"/{q}-" in n or f"/{q} " in n:
        return 7000
    if q in n:
        # Substring anywhere — penalize if query is only a small part of the name
        ratio = len(q) / len(n)
        if ratio >= 0.5:
            return 6000 + int(ratio * 1000)
        return 4000 + int(ratio * 1000)
    if q_norm in n_norm:
        ratio = len(q_norm) / len(n_norm)
        if ratio >= 0.5:
            return 3500 + int(ratio * 1000)
        return 2000 + int(ratio * 1000)
    # Check if query matches start of any word
    for sep in (" ", "-", "/"):
        if sep + q in n:
            return 1000
    return 0


def search_stations(query: str) -> list[dict]:
    """Fuzzy search MOSMIX stations by name, sorted by relevance."""
    stations = get_stations()
    scored = []
    for s in stations:
        score = _score_station_match(query, s.get("name", ""))
        if score > 0:
            scored.append((score, len(s.get("name", "")), s))
    # Sort by score descending, then name length ascending (shorter = more specific)
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [s for _, _, s in scored]


def find_nearest_station(lat: float, lon: float) -> dict:
    """Find the nearest MOSMIX station to given coordinates."""
    stations = get_stations()
    if not stations:
        return None
    nearest = min(stations, key=lambda s: haversine(lat, lon, s["lat"], s["lon"]))
    distance = haversine(lat, lon, nearest["lat"], nearest["lon"])
    return {**nearest, "distance_km": round(distance, 1)}


def get_station_by_id(station_id: str) -> dict:
    """Get station by ID."""
    stations = get_stations()
    for s in stations:
        if s["id"] == station_id:
            return s
    return None


def geocode_location(query: str, country: str = "Germany") -> dict:
    """Geocode a location name using Nominatim (OpenStreetMap).
    Returns {"lat": float, "lon": float, "display_name": str} or None.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{query}, {country}" if country else query,
        "format": "json",
        "limit": "1",
    }
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        full_url,
        headers={"User-Agent": "dwd-weather-skill/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and len(data) > 0:
                first = data[0]
                return {
                    "lat": float(first["lat"]),
                    "lon": float(first["lon"]),
                    "display_name": first.get("display_name", query),
                }
    except Exception:
        pass
    return None


def _cache_entry(result: dict) -> dict:
    """Create a minimal cacheable dict from a resolve result."""
    return {
        "id": result["id"],
        "name": result["name"],
        "lat": result["lat"],
        "lon": result["lon"],
        "elevation": result.get("elevation"),
        "matched_by": result.get("matched_by"),
        "geocoded_name": result.get("geocoded_name"),
        "distance_km": result.get("distance_km", 0.0),
    }


def clear_station_cache():
    """Clear the persistent station cache."""
    _ensure_cache_dir()
    if os.path.exists(STATION_CACHE_FILE):
        os.remove(STATION_CACHE_FILE)


def resolve_location(query: str) -> dict:
    """Resolve any location query to a MOSMIX station.

    Strategy:
    0. Check persistent cache (instant for repeated queries).
    1. If query looks like a station ID (alphanumeric, 2-8 chars), try direct ID lookup.
    2. Search MOSMIX station names by substring.
    3. If no direct match, geocode via Nominatim and find nearest MOSMIX station.

    Returns dict with keys: station_id, name, lat, lon, elevation,
    plus resolution metadata: matched_by ("id"|"name"|"geocode"),
    geocoded_name, distance_km (if geocoded).
    """
    query = query.strip()
    q_lower = query.lower()

    # 0. Check persistent cache
    cache = _load_station_cache()
    key = _cache_key(query)
    if key in cache:
        return cache[key]

    result = None

    # 1. Direct ID lookup (station IDs are typically 2-8 alphanumeric chars)
    if 2 <= len(query) <= 8 and query.replace("-", "").isalnum():
        s = get_station_by_id(query)
        if s:
            result = {
                **s,
                "matched_by": "id",
                "geocoded_name": None,
                "distance_km": 0.0,
            }

    # 2. Name search in MOSMIX stations
    if result is None:
        results = search_stations(query)
        if results:
            # Prefer exact match, then shortest name (most specific)
            exact = [r for r in results if r["name"].lower() == q_lower]
            if exact:
                best = exact[0]
            else:
                # Sort by name length (shorter = more likely exact city name)
                best = sorted(results, key=lambda r: len(r["name"]))[0]
            result = {
                **best,
                "matched_by": "name",
                "geocoded_name": None,
                "distance_km": 0.0,
            }

    # 3. Fallback: geocode via Nominatim, then find nearest station
    if result is None:
        geo = geocode_location(query)
        if geo:
            nearest = find_nearest_station(geo["lat"], geo["lon"])
            if nearest:
                result = {
                    **nearest,
                    "matched_by": "geocode",
                    "geocoded_name": geo["display_name"],
                    "distance_km": nearest["distance_km"],
                }

    if result is None:
        return None

    # Persist in cache
    cache[key] = _cache_entry(result)
    _save_station_cache(cache)
    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: dwd_stations.py <search|nearest|get|resolve> ...")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "search" and len(sys.argv) >= 3:
        q = sys.argv[2]
        results = search_stations(q)
        print(f"Found {len(results)} MOSMIX stations:")
        for r in results[:20]:
            print(f"  {r['id']:8s} {r['name']:35s} {r['lat']:8.4f} {r['lon']:8.4f}")
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
    elif cmd == "resolve" and len(sys.argv) >= 3:
        q = sys.argv[2]
        result = resolve_location(q)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"Could not resolve: {q}")
    else:
        print("Usage: dwd_stations.py <search QUERY|nearest LAT LON|get ID|resolve QUERY>")
