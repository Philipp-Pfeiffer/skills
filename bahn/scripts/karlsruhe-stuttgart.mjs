/**
 * Check Karlsruhe → Stuttgart departures with delays
 * 
 * FIXED: Uses realistic user-agent to avoid 403 blocks
 * FIXED: Falls back to dbnav profile if db profile fails
 */

import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

// Realistic user-agent to avoid API blocks
const USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

async function checkKarlsruheStuttgart(profile, profileName) {
  const client = createClient(profile, USER_AGENT);

  const { departures } = await client.departures('8000191', {
    when: new Date(),
    duration: 120,
    remarks: true
  });

  console.log(`Gefunden: ${departures.length} Abfahrten total (${profileName})\n`);

  // Zeige alle Richtungen zur Diagnose
  console.log('--- Alle Richtungen ---');
  departures.slice(0, 15).forEach(dep => {
    console.log(`${dep.plannedWhen?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })} — ${dep.line?.name || '?'} Richtung: ${dep.direction}`);
  });
  console.log('-----------------------\n');

  const toStuttgart = departures.filter(dep =>
    dep.direction?.toLowerCase().includes('stuttgart')
  );

  console.log(`Gefiltert nach Stuttgart: ${toStuttgart.length}\n`);

  if (toStuttgart.length === 0) {
    console.log('Keine direkten Verbindungen nach Stuttgart gefunden.');
    return;
  }

  toStuttgart.slice(0, 8).forEach((dep, i) => {
    const delayMin = dep.delay ? Math.round(dep.delay / 60) : 0;
    const status = dep.cancelled ? '❌ AUSFALL' :
                   delayMin === 0 ? 'pünktlich' :
                   delayMin <= 5 ? `+${delayMin} min` :
                   `+${delayMin} min VERSPÄTUNG`;

    const time = dep.plannedWhen?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' });
    const actualTime = dep.when?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' });

    let out = `${time} — ${dep.line?.name || '?'} nach Stuttgart`;
    if (dep.cancelled) {
      out += ` [${status}]`;
    } else if (delayMin > 0) {
      out += ` [Ankunft ${actualTime}, ${status}]`;
    } else {
      out += ` [${status}]`;
    }

    if (dep.platform) {
      out += ` — Gleis ${dep.platform}`;
    }

    console.log(out);
  });
}

async function main() {
  try {
    await checkKarlsruheStuttgart(dbProfile, 'db');
  } catch (err) {
    console.log(`db profile failed: ${err.message}`);
    console.log('Trying dbnav profile...\n');
    try {
      await checkKarlsruheStuttgart(dbnavProfile, 'dbnav');
    } catch (err2) {
      console.error(`Both profiles failed: ${err2.message}`);
      process.exit(1);
    }
  }
}

main().catch(console.error);
