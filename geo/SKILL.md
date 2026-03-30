---
name: geo
description: Geocoding, POI search, and station lookup using OpenStreetMap (Nominatim + Overpass). Use when users need to find coordinates for an address, find nearby places (restaurants, transit stops, parks, etc.), or find the nearest public transport station from an address. Supports integration with the Bahn skill for seamless "address → station → departures" workflows.
---

# Geo Skill

Geocoding, POI search, and public transport station lookup using OpenStreetMap.

## Services

- **Nominatim** — Address ↔ Coordinates (forward & reverse geocoding)
- **Overpass API** — POI search in radius (transit stops, restaurants, parks, etc.)
- **Station Bridge** — Address → nearest ÖPNV/Bahn station → DB station ID (via db-vendo-client)

## Rate Limits (Public APIs)

| Service | Limit | Key Required |
|---------|-------|-------------|
| Nominatim | 1 req/sec | No (User-Agent required) |
| Overpass | ~10k req/day | No |

For personal use (dozens of queries/day), these are more than sufficient. Add a 1-second delay between Nominatim calls if making multiple.

## Common Tasks

### 1. Geocode an Address

Find coordinates for a location name:

```bash
node scripts/geocode.mjs "Karlsruhe Europaplatz"
```

Response includes `lat`, `lon`, `name`, `type`, `address`, `importance`.

### 2. Reverse Geocode

Find address from coordinates:

```bash
node scripts/geocode.mjs --reverse 48.9917,8.3854
```

### 3. Find Nearby POIs

Search for places within a radius:

```bash
# All notable POIs within 500m
node scripts/nearby.mjs 48.9917 8.3854 500

# Specific category
node scripts/nearby.mjs 48.9917 8.3854 500 --tags "amenity=restaurant"

# Named tag with quotes
node scripts/nearby.mjs 48.9917 8.3854 1000 --tags '"shop"~"supermarket|convenience"'

# Presets (pre-built queries)
node scripts/nearby.mjs 48.9917 8.3854 500 --preset haltestellen
node scripts/nearby.mjs 48.9917 8.3854 500 --preset restaurants
node scripts/nearby.mjs 48.9917 8.3854 500 --preset mobilitaet
```

**Available presets:** `haltestellen`, `restaurants`, `cafes`, `supermarkets`, `pharmacies`, `atm`, `parks`, `mobilitaet`

Response includes `name`, `lat`, `lon`, `distance` (meters), `category`, `tags`.

### 4. Find Nearest Station from Address

Bridge between Geo and Bahn skills — resolves an address to the nearest ÖPNV/Bahn station:

```bash
node scripts/station-lookup.mjs "Karlsruhe Europaplatz"
node scripts/station-lookup.mjs "Karlsruhe Europaplatz" --radius 1000 --limit 5
node scripts/station-lookup.mjs --coords 48.9917,8.3854
```

Response includes:
- Nearby stations sorted by distance
- Top match with DB station ID (`recommendedDbId`) for use with Bahn skill
- Full DB station list for the top match

## Workflow: "Nächster Zug von Adresse X"

This is the key integration with the Bahn skill:

1. `station-lookup.mjs "Adresse"` → get `recommendedDbId`
2. Use that ID with Bahn skill's `check-delays.mjs` or `check-route.mjs`

Example:
```bash
# Step 1: Find nearest station
STATION_ID=$(node scripts/station-lookup.mjs "Karlsruhe Marktplatz" | jq -r '.topMatch.recommendedDbId')

# Step 2: Check departures (Bahn skill)
node ../bahn/scripts/check-delays.mjs $STATION_ID
```

## Notes

- All results are JSON to stdout. Progress/info goes to stderr.
- Nominatim returns importance scores — use these to disambiguate when multiple results match.
- Overpass queries can be slow for large radii (>2km). Keep radius reasonable.
- `station-lookup.mjs` requires `db-vendo-client` (same dependency as Bahn skill).
- For address input, Nominatim accepts street addresses, POI names, postal codes, cities — whatever you'd type into a maps search.

## Troubleshooting

**No results from geocoding?**
- Try more specific queries ("Karlsruhe Hbf" vs "Karlsruhe")
- Check spelling (German umlauts: ä, ö, ü)
- Try including the country for ambiguous names

**Overpass timeout?**
- Reduce radius
- Use `--tags` for specific categories instead of default (which queries all notable POIs)
- Overpass can be slow during peak hours — retry after a few seconds

**Station not found by station-lookup?**
- Increase `--radius` (default 750m, try 1500m for rural areas)
- Not all bus stops are in the DB HAFAS system — smaller stops may only appear in Overpass results
