#!/usr/bin/env node
/**
 * geocode.mjs — Address ↔ Coordinates via Nominatim (OSM)
 * 
 * Usage:
 *   node geocode.mjs "Karlsruhe Europaplatz"          # forward geocode
 *   node geocode.mjs --reverse 48.9917,8.3854          # reverse geocode
 *   node geocode.mjs --reverse 48.9917,8.3854 --limit 5
 */

const NOMINATIM_BASE = 'https://nominatim.openstreetmap.org';
const USER_AGENT = 'OpenClaw-GeoSkill/1.0';

async function forwardGeocode(query, { limit = 5, lang = 'de' } = {}) {
  const params = new URLSearchParams({
    q: query,
    format: 'jsonv2',
    limit: String(limit),
    'accept-language': lang,
    addressdetails: '1',
    extratags: '1',
    namedetails: '1',
  });

  const res = await fetch(`${NOMINATIM_BASE}/search?${params}`, {
    headers: { 'User-Agent': USER_AGENT },
  });

  if (!res.ok) throw new Error(`Nominatim error: ${res.status} ${res.statusText}`);

  const data = await res.json();
  return data.map(r => ({
    name: r.display_name,
    lat: parseFloat(r.lat),
    lon: parseFloat(r.lon),
    type: r.type,
    importance: r.importance,
    osmType: r.osm_type,
    osmId: r.osm_id,
    address: r.address,
    extra: r.extratags || {},
  }));
}

async function reverseGeocode(lat, lon, { limit = 1, lang = 'de' } = {}) {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    format: 'jsonv2',
    limit: String(limit),
    'accept-language': lang,
    addressdetails: '1',
    extratags: '1',
    namedetails: '1',
  });

  const res = await fetch(`${NOMINATIM_BASE}/reverse?${params}`, {
    headers: { 'User-Agent': USER_AGENT },
  });

  if (!res.ok) throw new Error(`Nominatim error: ${res.status} ${res.statusText}`);

  const data = await res.json();
  if (!data || data.error) return [];

  return [{
    name: data.display_name,
    lat: parseFloat(data.lat),
    lon: parseFloat(data.lon),
    type: data.type,
    importance: data.importance,
    osmType: data.osm_type,
    osmId: data.osm_id,
    address: data.address,
    extra: data.extratags || {},
  }];
}

// CLI
const args = process.argv.slice(2);
if (!args.length) {
  console.error('Usage: geocode.mjs <query> | geocode.mjs --reverse <lat>,<lon> [--limit N]');
  process.exit(1);
}

let isReverse = false;
let query = '';
let limit = 5;

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--reverse') {
    isReverse = true;
  } else if (args[i] === '--limit') {
    limit = parseInt(args[++i], 10);
  } else {
    query = args[i];
  }
}

try {
  let results;
  if (isReverse) {
    const [lat, lon] = query.split(',').map(Number);
    if (!lat || !lon) throw new Error('Invalid coordinates. Use format: lat,lon');
    results = await reverseGeocode(lat, lon, { limit });
  } else {
    results = await forwardGeocode(query, { limit });
  }

  if (!results.length) {
    console.log('No results found.');
    process.exit(0);
  }

  console.log(JSON.stringify(results, null, 2));
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
