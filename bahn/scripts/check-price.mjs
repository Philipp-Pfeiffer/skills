/**
 * Check ticket prices for routes
 * 
 * FIXED: Uses realistic user-agent to avoid 403 blocks
 * FIXED: Falls back to dbnav profile if db profile fails
 */

import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';
import { data as cards } from 'db-vendo-client/format/loyalty-cards.js';

// Realistic user-agent to avoid API blocks
const USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

async function checkPriceWithProfile(profile, fromId, toId, fromName, toName) {
  const client = createClient(profile, USER_AGENT);

  console.log(`\n💶 ${fromName} → ${toName}`);
  console.log(`Time: ${new Date().toLocaleString('de-DE')}\n`);

  const { journeys } = await client.journeys(fromId, toId, {
    departure: new Date(),
    results: 5
  });

  if (journeys.length === 0) {
    console.log('No connections found.');
    return;
  }

  console.log(`Found ${journeys.length} connections:\n`);

  journeys.forEach((j, i) => {
    const first = j.legs[0];
    const last = j.legs[j.legs.length - 1];
    const duration = Math.round((new Date(last.arrival) - new Date(first.departure)) / 60000);
    const changes = j.legs.filter(l => l.mode !== 'walking').length - 1;

    console.log(`${i + 1}. ${first.line?.name || 'Zug'}`);
    console.log(`   ${new Date(first.departure).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })} → ${new Date(last.arrival).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}`);
    console.log(`   ${duration} min, ${changes} Umst.`);
    
    if (j.price) {
      console.log(`   💶 ${j.price.amount} ${j.price.currency}`);
    } else {
      console.log(`   💶 Preis nicht verfügbar`);
    }
    console.log();
  });
}

async function checkPrice(fromId, toId, fromName, toName) {
  try {
    await checkPriceWithProfile(dbProfile, fromId, toId, fromName, toName);
  } catch (err) {
    console.log(`db profile failed: ${err.message}`);
    console.log('Trying dbnav profile...\n');
    try {
      await checkPriceWithProfile(dbnavProfile, fromId, toId, fromName, toName);
    } catch (err2) {
      console.error(`Both profiles failed: ${err2.message}`);
    }
  }
}

async function main() {
  await checkPrice('8000191', '8000096', 'Karlsruhe Hbf', 'Stuttgart Hbf');
  await checkPrice('8098160', '8000261', 'Berlin Hbf', 'München Hbf');
}

main().catch(console.error);
