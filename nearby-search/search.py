#!/usr/bin/env python3
"""
Nearby Search — Findet Orte in der Nähe via SerpAPI Google Maps.
Generisch für Cafés, Restaurants, Bäckereien oder beliebige POIs.

Usage:
  python search.py <lat> <lon> ["query"] [radius_m]
  python search.py kit "Café" 1000          # nutzt Alias aus locations.json
  python search.py home "Restaurant" 2000   # nutzt Alias
"""

import sys
import os
import json
import math
import re
import requests

def parse_natural_query(text):
    """Extrahiert Standort, Query und Radius aus natürlicher Sprache.
    
    Beispiele:
      'ich bin am kit und will frühstücken' → ('kit', 'Frühstück', 1500)
      'Cafés in der Nähe von 49.009, 8.418' → ('49.009, 8.418', 'Café', 1500)
      'ich bin morgen in berlin hbf und will chinesisch essen in 500m' → ('berlin hbf', 'Chinesisches Restaurant', 500)
      'Restaurants nah am kit' → ('kit', 'Restaurant', 500)
    """
    text_lower = text.lower()
    
    # --- Radius extrahieren ---
    radius = 1500  # Default
    
    # Explizite Distanz: "in 500m", "500 meter", "1km"
    dist_match = re.search(r'(?:in\s+)?(\d+)\s*(m|meter|km|kilometer)', text_lower)
    if dist_match:
        val = int(dist_match.group(1))
        unit = dist_match.group(2)
        radius = val * 1000 if unit in ('km', 'kilometer') else val
    
    # Implizite Distanz
    if any(w in text_lower for w in ['nah', 'in der nähe', 'um die ecke', 'umme ecke']):
        radius = 500
    if any(w in text_lower for w in ['weit weg', 'großer radius', 'weit', 'weiter']):
        radius = 3000
    
    # --- Query extrahieren (zuerst, damit food_types für Orts-Filter verfügbar) ---
    query = None
    
    # Essens-Typen
    food_types = {
        'frühstück': 'Frühstück',
        'frühstücken': 'Frühstück',
        'breakfast': 'Frühstück',
        'mittagessen': 'Mittagessen',
        'lunch': 'Mittagessen',
        'abendessen': 'Abendessen',
        'dinner': 'Abendessen',
        'essen': 'Restaurant',
        'cafe': 'Café',
        'café': 'Café',
        'kaffee': 'Café',
        'bäckerei': 'Bäckerei',
        'bakery': 'Bäckerei',
        'restaurant': 'Restaurant',
        'pizza': 'Pizza',
        'burger': 'Burger',
        'chinesisch': 'Chinesisches Restaurant',
        'chinese': 'Chinesisches Restaurant',
        'italienisch': 'Italienisches Restaurant',
        'italian': 'Italienisches Restaurant',
        'indisch': 'Indisches Restaurant',
        'indian': 'Indisches Restaurant',
        'sushi': 'Sushi',
        'japanisch': 'Japanisches Restaurant',
        'japanese': 'Japanisches Restaurant',
        'mexikanisch': 'Mexikanisches Restaurant',
        'mexican': 'Mexikanisches Restaurant',
        'thailändisch': 'Thailändisches Restaurant',
        'thai': 'Thailändisches Restaurant',
        'vietnamesisch': 'Vietnamesisches Restaurant',
        'vietnamese': 'Vietnamesisches Restaurant',
        'döner': 'Döner',
        'kebap': 'Döner',
        'gyros': 'Griechisches Restaurant',
        'griechisch': 'Griechisches Restaurant',
        'greek': 'Griechisches Restaurant',
        'spanisch': 'Spanisches Restaurant',
        'spanish': 'Spanisches Restaurant',
        'tapas': 'Tapas',
        'steak': 'Steakhouse',
        'steakhouse': 'Steakhouse',
        'vegan': 'Veganes Restaurant',
        'vegetarisch': 'Vegetarisches Restaurant',
        'vegetarian': 'Vegetarisches Restaurant',
        'glutenfrei': 'Glutenfreies Restaurant',
        'gluten-free': 'Glutenfreies Restaurant',
    }
    
    # Sortiere nach Länge absteigend: längere/specifischere Keywords zuerst
    for keyword, q in sorted(food_types.items(), key=lambda x: -len(x[0])):
        if keyword in text_lower:
            query = q
            break
    
    # Fallback: "Orte in der Nähe", "was gibt es", "wo kann ich"
    if not query:
        if any(w in text_lower for w in ['cafe', 'café', 'kaffee', 'kaffeehaus']):
            query = 'Café'
        elif any(w in text_lower for w in ['restaurant', 'essen', 'gaststätte', 'lokal']):
            query = 'Restaurant'
        elif any(w in text_lower for w in ['bäckerei', 'brot', 'brötchen']):
            query = 'Bäckerei'
        elif any(w in text_lower for w in ['bar', 'kneipe', 'pub']):
            query = 'Bar'
        else:
            query = 'Café'  # Ultimate fallback
    
    # --- Standort extrahieren ---
    location = None
    
    # Bekannte Aliasse
    locations = load_locations()
    for alias in locations.keys():
        # Prüfe auf "am [alias]", "in [alias]", "bei [alias]", "nahe [alias]"
        pattern = rf'\b(?:am|in|bei|nahe|bei der|an der)\s+{re.escape(alias)}\b'
        if re.search(pattern, text_lower):
            location = alias
            break
    
    # Unbekannte Orte: "in [Stadt/Ort]", "bei [Ort]", "nahe [Ort]"
    if not location:
        # Suche nach "in berlin", "in stuttgart hbf", "bei münchen"
        # Stoppe bei bekannten Nicht-Orts-Wörtern
        stopwords = {'und', 'will', 'suche', 'brauche', 'möchte', 'willst', 
                     'ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'sie',
                     'der', 'die', 'das', 'ein', 'eine', 'mit', 'für', 'von',
                     'zu', 'auf', 'an', 'aus', 'nach', 'bei', 'in', 'um',
                     'am', 'zum', 'zur', 'durch', 'über', 'unter', 'vor',
                     'hinter', 'neben', 'zwischen', 'gegen', 'ohne', 'während',
                     'weil', 'dass', 'wenn', 'als', 'wie', 'wo', 'was', 'wer',
                     'gibt', 'gib', 'habe', 'hat', 'ist', 'sind', 'war', 'waren'}
        
        place_match = re.search(r'\b(?:in|bei|nahe|an)\s+([a-zäöüß]+(?:\s+[a-zäöüß]+){0,2})\b', text_lower)
        if place_match:
            candidate = place_match.group(1).strip()
            # Entferne Stopwörter vom Ende
            words = candidate.split()
            while words and words[-1] in stopwords:
                words.pop()
            candidate = ' '.join(words)
            
            if candidate and candidate not in food_types and len(candidate) > 2:
                location = candidate
    
    # Koordinaten direkt: "49.009, 8.418" oder "49.009 8.418"
    if not location:
        coord_match = re.search(r'(-?\d+\.\d+)[,\s]+(-?\d+\.\d+)', text)
        if coord_match:
            location = f"{coord_match.group(1)} {coord_match.group(2)}"
    
    # Fallback: Standard-Standort (z.B. "kit" wenn nichts angegeben)
    if not location:
        # Versuche erste bekannte Location im Text zu finden
        for alias in locations.keys():
            if alias in text_lower:
                location = alias
                break
    
    return location, query, radius

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(SCRIPT_DIR, "config")
SERPAPI_FILE = os.path.join(CONFIG_DIR, "serpapi.env")
LOCATIONS_FILE = os.path.join(CONFIG_DIR, "locations.json")


def load_api_key():
    if not os.path.exists(SERPAPI_FILE):
        print(f"❌ Config fehlt: {SERPAPI_FILE}")
        print("   Kopiere config/example.serpapi.env → config/serpapi.env und trage deinen Key ein.")
        sys.exit(1)
    with open(SERPAPI_FILE) as f:
        for line in f:
            line = line.strip()
            if line.startswith("SERPAPI_KEY="):
                return line.split("=", 1)[1].strip('"\'')
    print("❌ SERPAPI_KEY nicht in config/serpapi.env gefunden.")
    sys.exit(1)


def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return {}
    with open(LOCATIONS_FILE) as f:
        return json.load(f)


def geocode_place(query):
    """Geocodet einen Ortsnamen via OpenStreetMap Nominatim zu Koordinaten."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    try:
        r = requests.get(url, params=params, timeout=10, headers={"User-Agent": "nearby-search-skill/1.0"})
        data = r.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"]), data[0].get("display_name", query)
    except Exception as e:
        pass
    return None


def resolve_location(arg):
    """Löst ein Argument zu (lat, lon) auf. Kann ein Alias, direkte Koordinaten, oder ein Ortsname sein."""
    # Versuche als Alias
    locations = load_locations()
    alias = locations.get(arg.lower())
    if alias:
        return alias["lat"], alias["lon"], alias.get("label", arg)

    # Versuche als lat,lon Paar
    try:
        parts = arg.replace(",", " ").split()
        if len(parts) == 2:
            return float(parts[0]), float(parts[1]), arg
    except ValueError:
        pass

    # Versuche als Ortsname zu geocoden (z.B. "Berlin HBF", "Stuttgart Hauptbahnhof")
    coords = geocode_place(arg)
    if coords:
        return coords

    print(f"❌ Standort nicht erkannt: '{arg}'")
    print(f"   Bekannte Aliasse: {', '.join(locations.keys()) if locations else 'keine'}")
    print("   Oder gib Koordinaten an: 49.009 8.418")
    sys.exit(1)


def haversine(lat1, lon1, lat2, lon2):
    """Distanz in Metern zwischen zwei GPS-Koordinaten."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a)))



def reverse_geocode_city(lat, lon):
    """Ermittelt den Stadtnamen aus Koordinaten via OpenStreetMap Nominatim."""
    url = f"https://nominatim.openstreetmap.org/reverse"
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10, "addressdetails": 1}
    try:
        r = requests.get(url, params=params, timeout=10, headers={"User-Agent": "nearby-search-skill/1.0"})
        data = r.json()
        addr = data.get("address", {})
        # Versuche verschiedene Stadtfelder
        city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("municipality")
        if city:
            return city
        # Fallback: display_name extrahieren
        display = data.get("display_name", "")
        parts = display.split(", ")
        if len(parts) >= 2:
            return parts[1].strip()
    except Exception:
        pass
    return None


def search_google_maps(query, api_key, lat=None, lon=None):
    """Fragt SerpAPI Google Maps an. Fügt Stadtnamen zum Query hinzu wenn verfügbar."""
    # Reverse Geocoding für Stadtnamen
    city = None
    if lat and lon:
        city = reverse_geocode_city(lat, lon)
    
    full_query = f"{query} {city}" if city else query
    
    params = {
        "engine": "google_maps",
        "q": full_query,
        "type": "search",
        "api_key": api_key,
    }
    r = requests.get("https://serpapi.com/search.json", params=params, timeout=30)
    data = r.json()
    if data.get("error"):
        print(f"❌ SerpAPI Fehler: {data['error']}")
        sys.exit(1)
    return data.get("local_results", [])


def format_list(places):
    """Gibt Ergebnisse als WhatsApp-kompatible Liste aus."""
    if not places:
        print("Keine Ergebnisse im gewählten Radius gefunden.")
        return

    print(f"\nGefunden: {len(places)} Orte\n")
    for i, p in enumerate(places, 1):
        rating = f"⭐ {p['rating']:.1f}" if p.get("rating") else "⭐ -"
        reviews = f"({p['reviews']} Reviews)" if p.get("reviews") else ""
        dist = f"📍 {p['distance']}m"
        specialty = f"— {p['type']}" if p.get("type") else ""
        print(f"{i}. {p['name']} {rating} {reviews} {dist} {specialty}".strip())


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python search.py <lat> <lon> [\"query\"] [radius_m]")
        print("  python search.py kit \"Café\" 1000")
        print("  python search.py 49.009 8.418 \"Restaurant\" 2000")
        print()
        print("  # Natürliche Sprache (ein Argument):")
        print('  python search.py "ich bin am kit und will frühstücken"')
        print('  python search.py "chinesisches essen in berlin hbf in 500m"')
        sys.exit(1)

    # Prüfe ob erstes Argument natürliche Sprache ist (mehr als 2 Wörter)
    first_arg = sys.argv[1]
    if len(first_arg.split()) > 2 and not re.match(r'^-?\d', first_arg):
        # Natürliche Sprache
        text = first_arg
        location_alias, query, radius = parse_natural_query(text)
        
        if not location_alias:
            print("❌ Standort nicht erkannt. Bekannte Orte:")
            for a, info in load_locations().items():
                print(f"   {a} → {info['label']}")
            print("   Oder gib Koordinaten an: 49.009 8.418")
            sys.exit(1)
        
        lat, lon, label = resolve_location(location_alias)
        print(f"🔍 Erkannt: Standort='{label}', Suche='{query}', Radius={radius}m")
    else:
        # Klassische Args: location [query] [radius]
        loc_arg = sys.argv[1]
        lat, lon, label = resolve_location(loc_arg)
        query = sys.argv[2] if len(sys.argv) > 2 else "Café"
        radius = 1500
        if len(sys.argv) > 3:
            try:
                radius = int(sys.argv[3])
            except ValueError:
                pass
        
        # Falls 2. Arg eigentlich Radius ist (kein Leerzeichen drin → keine Query)
        if len(sys.argv) == 3:
            try:
                radius = int(sys.argv[2])
                query = "Café"
            except ValueError:
                pass

    print(f"🔍 Suche nach '{query}' im Radius von {radius}m um {label} ({lat}, {lon})...")

    api_key = load_api_key()
    results = search_google_maps(query, api_key, lat, lon)

    places = []
    for p in results:
        coords = p.get("gps_coordinates", {})
        plat, plon = coords.get("latitude"), coords.get("longitude")
        if plat is None or plon is None:
            continue

        dist = haversine(lat, lon, plat, plon)
        if dist <= radius:
            places.append({
                "name": p.get("title", "Unbekannt"),
                "type": p.get("type", ""),
                "rating": p.get("rating"),
                "reviews": p.get("reviews"),
                "distance": dist,
            })

    places.sort(key=lambda x: x["distance"])
    format_list(places)


if __name__ == "__main__":
    main()
