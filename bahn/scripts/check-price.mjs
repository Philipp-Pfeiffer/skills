/**
 * Example: Check ticket prices with Bahncard options
 * Using Deutsche Bahn API for pricing information with loyalty cards
 */

import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';
import { data as cards } from 'db-vendo-client/format/loyalty-cards.js';

async function checkPriceWithBahncard(fromId, fromName, toId, toName) {
  const client = createClient(dbnavProfile, 'clawdbot-bahn-skill');

  console.log(`\n💰 Checking prices: ${fromName} → ${toName}`);
  console.log(`Time: ${new Date().toLocaleString('de-DE')}\n`);

  // Get journeys
  const { journeys } = await client.journeys(fromId, toId, {
    departure: new Date(),
    results: 5
  });

  if (journeys.length === 0) {
    console.log('No connections found.');
    return;
  }

  console.log(`Found ${journeys.length} connections:\n`);

  // For each journey, get prices with different Bahncard options
  for (let i = 0; i < Math.min(journeys.length, 5); i++) {
    const journey = journeys[i];
    const firstLeg = journey.legs[0];
    const departureTime = firstLeg.departure?.toLocaleString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    });
    const trainName = firstLeg.line?.name || 'Unknown';

    console.log(`${i + 1}. ${trainName} (${departureTime})`);

    // Get pricing for different options
    const priceOptions = [];

    // Regular price
    try {
      const { journeys: regular } = await client.journeys(fromId, toId, {
        departure: firstLeg.plannedDeparture || firstLeg.departure,
        results: 1
      });
      if (regular[0]?.price) {
        priceOptions.push({
          name: 'Regular',
          price: regular[0].price.amount
        });
      }
    } catch (e) {
      // Skip if pricing fails
    }

    // Bahncard 25
    try {
      const { journeys: bc25 } = await client.journeys(fromId, toId, {
        departure: firstLeg.plannedDeparture || firstLeg.departure,
        results: 1,
        loyaltyCard: {
          type: cards.BAHNCARD,
          discount: 25,
          class: 2
        }
      });
      if (bc25[0]?.price) {
        priceOptions.push({
          name: 'BC 25',
          price: bc25[0].price.amount
        });
      }
    } catch (e) {
      // Skip if pricing fails
    }

    // Bahncard 50
    try {
      const { journeys: bc50 } = await client.journeys(fromId, toId, {
        departure: firstLeg.plannedDeparture || firstLeg.departure,
        results: 1,
        loyaltyCard: {
          type: cards.BAHNCARD,
          discount: 50,
          class: 2
        }
      });
      if (bc50[0]?.price) {
        priceOptions.push({
          name: 'BC 50',
          price: bc50[0].price.amount
        });
      }
    } catch (e) {
      // Skip if pricing fails
    }

    // Display prices
    if (priceOptions.length > 0) {
      const regularPrice = priceOptions.find(p => p.name === 'Regular')?.price;
      
      priceOptions.forEach(option => {
        const savings = regularPrice && option.price !== regularPrice
          ? (regularPrice - option.price).toFixed(2)
          : null;
        
        if (option.name === 'Regular') {
          console.log(`   🎫 Regular:  ${option.price.toFixed(2)} EUR`);
        } else if (savings && parseFloat(savings) > 0) {
          console.log(`   💳 ${option.name.padEnd(8)} ${option.price.toFixed(2)} EUR (save ${savings} EUR)`);
        } else {
          console.log(`   💳 ${option.name.padEnd(8)} ${option.price.toFixed(2)} EUR`);
        }
      });
    } else {
      console.log(`   💵 Price: Not available`);
    }

    // Duration
    if (journey.duration) {
      const durationMin = Math.round(journey.duration / 60000);
      console.log(`   ⏱️  Duration: ${durationMin} minutes`);
    }

    // Changes
    const changes = journey.legs.length - 1;
    console.log(`   🔄 Changes: ${changes}`);

    console.log();
  }
}

async function main() {
  // Example: Check prices for major routes with Bahncard options
  await checkPriceWithBahncard('8098160', 'Berlin Hbf', '8000261', 'München Hbf');
}

main().catch(console.error);
