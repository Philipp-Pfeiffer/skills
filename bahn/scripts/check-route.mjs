/**
 * Check departures from origin to destination
 * Demonstrates filtering for specific directions
 * 
 * FIXED: Uses realistic user-agent to avoid 403 blocks
 * FIXED: Falls back to dbnav profile if db profile fails
 */

import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

// Realistic user-agent to avoid API blocks
const USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

async function checkRouteWithProfile(profile, profileName, fromId, toName) {
  const client = createClient(profile, USER_AGENT);

  console.log(`\n🚄 ${toName} (via ${profileName})`);
  console.log(`Time: ${new Date().toLocaleString('de-DE')}\n`);

  const { departures } = await client.departures(fromId, {
    when: new Date(),
    duration: 120,
    remarks: true
  });

  // Filter for trains going to destination
  const toDestination = departures.filter(dep =>
    dep.direction?.toLowerCase().includes(toName.toLowerCase())
  );

  console.log(`Found ${toDestination.length} direct connections to ${toName}:\n`);

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
    console.log(`   → ${toName}`);
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

async function checkRoute() {
  try {
    await checkRouteWithProfile(dbProfile, 'db', '8098160', 'München');
  } catch (err) {
    console.log(`db profile failed: ${err.message}`);
    console.log('Trying dbnav profile...\n');
    try {
      await checkRouteWithProfile(dbnavProfile, 'dbnav', '8098160', 'München');
    } catch (err2) {
      console.error(`Both profiles failed: ${err2.message}`);
      process.exit(1);
    }
  }
}

checkRoute().catch(console.error);
