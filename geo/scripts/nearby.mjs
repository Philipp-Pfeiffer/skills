#!/usr/bin/env node
/**
 * nearby.mjs — POI search via Overpass API (OSM)
 * 
 * Usage:
 *   node nearby.mjs 48.9917 8.3854 500 --tags "amenity=restaurant" --limit 10
 *   node nearby.mjs 48.9917 8.3854 500 --tags "public_transport=station" --limit 5
 *   node nearby.mjs 48.9917 8.3854 1000 --preset "haltestellen"
 */

const OVERPASS_SERVERS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
];

// Common presets
const PRESETS = {
  haltestellen: [
    'nwr["public_transport"~"stop_position|station|platform"](around:RADIUS,LAT,LON);',
    'node["highway"="bus_stop"](around:RADIUS,LAT,LON);',
  ],
  restaurants: ['nwr["amenity"="restaurant"](around:RADIUS,LAT,LON);'],
  cafes: ['nwr["amenity"="cafe"](around:RADIUS,LAT,LON);'],
  supermarkets: ['nwr["shop"~"supermarket|convenience"](around:RADIUS,LAT,LON);'],
  pharmacies: ['nwr["amenity"="pharmacy"](around:RADIUS,LAT,LON);'],
  atm: ['nwr["amenity"="atm"](around:RADIUS,LAT,LON);'],
  parks: ['way["leisure"="park"](around:RADIUS,LAT,LON);'],
  // Combo preset for mobility
  mobilitaet: [
    'nwr["public_transport"~"stop_position|station|platform"](around:RADIUS,LAT,LON);',
    'node["highway"="bus_stop"](around:RADIUS,LAT,LON);',
    'node["amenity"="bicycle_rental"](around:RADIUS,LAT,LON);',
    'nwr["amenity"="car_sharing"](around:RADIUS,LAT,LON);',
  ],
};

function buildQuery(lat, lon, radius, tagFilter, preset) {
  let statements = [];

  if (preset && PRESETS[preset]) {
    statements = PRESETS[preset].map(s =>
      s.replace('RADIUS', String(radius)).replace('LAT', String(lat)).replace('LON', String(lon))
    );
  } else if (tagFilter) {
    statements.push(
      `nwr[${tagFilter}](around:${radius},${lat},${lon});`
    );
  } else {
    // Default: all notable POIs
    const defaultTags = [
      'amenity', 'shop', 'tourism', 'leisure',
      'public_transport', 'highway', 'office',
    ];
    for (const tag of defaultTags) {
      statements.push(
        `nwr[${tag}](around:${radius},${lat},${lon});`
      );
    }
  }

  const out = statements.join('\n');
  return `
[out:json][timeout:25];
(
  ${out}
);
out center tags 50;
`.trim();
}

async function queryOverpass(lat, lon, radius, { tagFilter, preset, limit } = {}) {
  const query = buildQuery(lat, lon, radius, tagFilter, preset);

  let lastError;
  for (const server of OVERPASS_SERVERS) {
    try {
      const res = await fetch(server, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `data=${encodeURIComponent(query)}`,
      });

      if (!res.ok) throw new Error(`Overpass error: ${res.status} ${res.statusText}`);
      return await res.json();
    } catch (err) {
      lastError = err;
      continue;
    }
  }
  throw new Error(`All Overpass servers failed. Last: ${lastError.message}`);

  const data = await res.json();

  // Calculate distance from center for each element
  const results = (data.elements || []).map(el => {
    const elLat = el.lat || el.center?.lat;
    const elLon = el.lon || el.center?.lon;

    // Haversine distance
    const dist = elLat ? haversine(lat, lon, elLat, elLon) : null;

    const tags = el.tags || {};
    const name = tags.name || tags['name:de'] || null;
    const type = el.type;

    return {
      id: el.id,
      osmType: type,
      name,
      lat: elLat,
      lon: elLon,
      distance: dist ? Math.round(dist) : null, // meters
      tags,
      // Convenience fields
      category: tags.amenity || tags.shop || tags.tourism || tags.leisure || tags.public_transport || tags.highway || null,
    };
  });

  // Filter out unnamed entries for most queries, sort by distance
  let filtered = results.filter(r => r.name || r.category === 'bus_stop');
  filtered.sort((a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity));

  if (limit) filtered = filtered.slice(0, limit);

  return filtered;
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth radius in meters
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// CLI
const args = process.argv.slice(2);
if (args.length < 3) {
  console.error(`Usage: nearby.mjs <lat> <lon> <radius_m> [--tags "key=value"] [--preset NAME] [--limit N]`);
  console.error(`Presets: ${Object.keys(PRESETS).join(', ')}`);
  process.exit(1);
}

const lat = parseFloat(args[0]);
const lon = parseFloat(args[1]);
const radius = parseInt(args[2], 10);
let tagFilter = null;
let preset = null;
let limit = 20;

for (let i = 3; i < args.length; i++) {
  if (args[i] === '--tags' && args[++i]) tagFilter = args[i];
  else if (args[i] === '--preset' && args[++i]) preset = args[i];
  else if (args[i] === '--limit' && args[++i]) limit = parseInt(args[i], 10);
}

if (!lat || !lon || !radius) {
  console.error('Invalid lat, lon, or radius.');
  process.exit(1);
}

try {
  const results = await queryOverpass(lat, lon, radius, { tagFilter, preset, limit });

  if (!results.length) {
    console.log('No results found.');
    process.exit(0);
  }

  console.log(JSON.stringify(results, null, 2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
