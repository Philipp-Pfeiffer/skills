#!/usr/bin/env node
/**
 * station-lookup.mjs — Find nearest public transport station from an address
 * Bridge between Geo-Skill (Nominatim + Overpass) and Bahn-Skill (db-vendo-client)
 * 
 * Usage:
 *   node station-lookup.mjs "Karlsruhe Europaplatz"
 *   node station-lookup.mjs "Karlsruhe Europaplatz" --radius 1000 --limit 5
 *   node station-lookup.mjs --coords 48.9917,8.3854
 */

import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';
const OVERPASS_SERVERS = [
  'https://overpass-api.de/api/interpreter',
  'https://overpass.kumi.systems/api/interpreter',
  'https://maps.mail.ru/osm/tools/overpass/api/interpreter',
];
const USER_AGENT = 'OpenClaw-GeoSkill/1.0';

async function geocodeAddress(query) {
  const params = new URLSearchParams({
    q: query,
    format: 'jsonv2',
    limit: '1',
    'accept-language': 'de',
    addressdetails: '1',
  });

  const res = await fetch(`${NOMINATIM_BASE}/search?${params}`, {
    headers: { 'User-Agent': USER_AGENT },
  });

  if (!res.ok) throw new Error(`Nominatim error: ${res.status}`);
  const data = await res.json();
  if (!data.length) throw new Error(`Address not found: ${query}`);
  return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon), name: data[0].display_name };
}

async function findNearbyStations(lat, lon, radius = 750, limit = 5) {
  const query = `
[out:json][timeout:25];
(
  node["railway"="station"](around:${radius},${lat},${lon});
  node["public_transport"="station"](around:${radius},${lat},${lon});
  node["railway"="halt"](around:${radius},${lat},${lon});
  node["public_transport"="stop_position"](around:${radius},${lat},${lon});
  node["highway"="bus_stop"](around:${radius},${lat},${lon});
);
out center tags;
`.trim();

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

  return (data.elements || [])
    .map(el => {
      const tags = el.tags || {};
      const elLat = el.lat || el.center?.lat;
      const elLon = el.lon || el.center?.lon;
      const dist = elLat ? haversine(lat, lon, elLat, elLon) : null;

      return {
        name: tags.name || null,
        lat: elLat,
        lon: elLon,
        distance: dist ? Math.round(dist) : null,
        railway: tags.railway || null,
        publicTransport: tags.public_transport || null,
        trainName: tags.uic_ref || tags.ref || null,
        operator: tags.operator || null,
        osmType: el.type,
        osmId: el.id,
      };
    })
    .filter(r => r.name && r.distance !== null)
    .sort((a, b) => a.distance - b.distance)
    .slice(0, limit);
}

async function lookupDbStation(stationName) {
  const client = createClient(dbnavProfile, USER_AGENT);
  const locations = await client.locations(stationName, { results: 3 });
  return locations.map(loc => ({
    name: loc.name || loc.address,
    id: loc.id,
    type: loc.type,
    distance: loc.distance ? Math.round(loc.distance) : null,
  }));
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// CLI
const args = process.argv.slice(2);
if (!args.length) {
  console.error('Usage: station-lookup.mjs <address> | station-lookup.mjs --coords <lat>,<lon>');
  process.exit(1);
}

let lat = null, lon = null;
let addressQuery = null;
let radius = 750;
let limit = 5;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--coords' && args[++i]) {
    [lat, lon] = args[i].split(',').map(Number);
  } else if (args[i] === '--radius' && args[++i]) {
    radius = parseInt(args[i], 10);
  } else if (args[i] === '--limit' && args[++i]) {
    limit = parseInt(args[i], 10);
  } else if (!args[i].startsWith('--')) {
    addressQuery = args[i];
  }
}

try {
  // Step 1: Get coordinates
  if (!lat || !lon) {
    if (!addressQuery) throw new Error('Provide an address or --coords');
    const geo = await geocodeAddress(addressQuery);
    lat = geo.lat;
    lon = geo.lon;
    console.error(`📍 Geocoded: ${geo.name}`);
  }

  // Step 2: Find nearby stations via Overpass
  console.error(`🔍 Searching ${radius}m radius...`);
  const stations = await findNearbyStations(lat, lon, radius, limit);

  if (!stations.length) {
    console.log(JSON.stringify({ coordinates: { lat, lon }, stations: [], message: `No stations found within ${radius}m. Try larger radius.` }));
    process.exit(0);
  }

  // Step 3: For top result, look up DB station ID
  const topStation = stations[0];
  let dbStations = [];
  try {
    dbStations = await lookupDbStation(topStation.name);
  } catch (e) {
    console.error(`⚠️  DB lookup failed for "${topStation.name}": ${e.message}`);
  }

  const output = {
    coordinates: { lat, lon },
    query: addressQuery || `${lat},${lon}`,
    stations: stations,
    topMatch: {
      name: topStation.name,
      distance: topStation.distance,
      dbStations: dbStations,
      recommendedDbId: dbStations.length > 0 ? dbStations[0].id : null,
    },
  };

  console.log(JSON.stringify(output, null, 2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
