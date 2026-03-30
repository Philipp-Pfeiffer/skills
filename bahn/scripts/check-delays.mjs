/**
 * Example: How to check if your train/bus is on time
 * Using Deutsche Bahn API for real-time delay data
 */

import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

async function checkDelays(stationId, stationName) {
  const client = createClient(dbnavProfile, 'clawdbot-bahn-skill');

  console.log(`\n🚄 Checking departures for ${stationName}...`);
  console.log(`Station ID: ${stationId}`);
  console.log(`Time: ${new Date().toLocaleString('de-DE')}\n`);

  const { departures } = await client.departures(stationId, {
    when: new Date(),
    duration: 60, // next 60 minutes
    remarks: true
  });

  if (departures.length === 0) {
    console.log('No departures found in the next hour.');
    return;
  }

  console.log(`Found ${departures.length} departures:\n`);

  departures.slice(0, 8).forEach((dep, i) => {
    const delayMin = dep.delay ? Math.round(dep.delay / 60) : 0;
    const status = dep.cancelled ? '❌ CANCELLED' :
                   delayMin === 0 ? '✅ On time' :
                   delayMin <= 2 ? '⚠️  Small delay' :
                   '⚠️  Delayed';

    console.log(`${i + 1}. ${dep.line?.name || dep.line?.id || '?'}`);
    console.log(`   → ${dep.direction || 'Unknown destination'}`);
    console.log(`   🕐 ${dep.plannedWhen?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}`);
    console.log(`   ${status}`);

    if (dep.delay && dep.delay > 0) {
      console.log(`   Delay: ${delayMin} min (${dep.delay}s)`);
      console.log(`   Expected: ${dep.when?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}`);
    }

    if (dep.remarks && dep.remarks.length > 0) {
      console.log(`   ℹ️  ${dep.remarks.length} remark(s)`);
    }

    console.log();
  });
}

async function main() {
  // Example: Check major stations
  await checkDelays('8098160', 'Berlin Hbf');
  await checkDelays('8000261', 'München Hbf');
}

main().catch(console.error);
