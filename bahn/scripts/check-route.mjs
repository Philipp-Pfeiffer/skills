/**
 * Example: Check departures from origin to destination
 * Demonstrates filtering for specific directions
 */

import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

async function checkRoute() {
  const client = createClient(dbnavProfile, 'clawdbot-bahn-skill');

  console.log(`\n🚄 Berlin Hbf → München Hbf`);
  console.log(`Time: ${new Date().toLocaleString('de-DE')}\n`);

  const { departures } = await client.departures('8098160', { // Berlin Hbf
    when: new Date(),
    duration: 120,
    remarks: true
  });

  // Filter for trains going to München
  const toDestination = departures.filter(dep =>
    dep.direction?.toLowerCase().includes('münchen') ||
    dep.direction?.toLowerCase().includes('munich')
  );

  console.log(`Found ${toDestination.length} direct connections to München:\n`);

  if (toDestination.length === 0) {
    console.log('No direct connections found. Showing all departures:\n');
    departures.slice(0, 10).forEach((dep, i) => {
      const delayMin = dep.delay ? Math.round(dep.delay / 60) : 0;
      const status = dep.cancelled ? '❌ CANCELLED' :
                     delayMin === 0 ? '✅ On time' :
                     delayMin <= 5 ? '⚠️  Small delay' :
                     '⚠️  Delayed';

      console.log(`${i + 1}. ${dep.line?.name || dep.line?.id || '?'}`);
      console.log(`   → ${dep.direction || 'Unknown'}`);
      console.log(`   🕐 ${dep.plannedWhen?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' })}`);
      console.log(`   ${status}`);
      
      if (dep.delay && dep.delay > 0) {
        console.log(`   Delay: ${delayMin} min`);
      }
      console.log();
    });
    return;
  }

  toDestination.slice(0, 8).forEach((dep, i) => {
    const delayMin = dep.delay ? Math.round(dep.delay / 60) : 0;
    const status = dep.cancelled ? '❌ CANCELLED' :
                   delayMin === 0 ? '✅ On time' :
                   delayMin <= 5 ? '⚠️  Small delay' :
                   '⚠️  Delayed';

    console.log(`${i + 1}. ${dep.line?.name || dep.line?.id || '?'}`);
    console.log(`   → München Hbf`);
    console.log(`   🕐 ${dep.plannedWhen?.toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit', weekday: 'short', day: '2-digit', month: '2-digit' })}`);
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

checkRoute().catch(console.error);
