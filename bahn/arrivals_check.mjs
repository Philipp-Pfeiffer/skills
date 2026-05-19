import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';

const client = createClient(dbProfile, 'openclaw-bahn-check');

const stationId = '8005769'; // Stuttgart-Bad Cannstatt (correct ID)
const when = new Date('2026-05-03T16:00:00+02:00');

// Check available methods
const methods = Object.keys(client).filter(k => typeof client[k] === 'function');
const relevant = methods.filter(m => ['departures', 'arrivals', 'journeys', 'locations'].includes(m));
console.log('Available methods:', relevant);

try {
  if (client.arrivals) {
    console.log('\n=== ARRIVALS (16:00 - 16:30) ===');
    const result = await client.arrivals(stationId, { when, duration: 30 });
    const arrivals = result.arrivals || [];
    console.log(`Found ${arrivals.length} arrivals`);
    
    arrivals.forEach(a => {
      const planned = new Date(a.plannedWhen);
      const hour = planned.getHours();
      const min = planned.getMinutes().toString().padStart(2, '0');
      const delay = a.delay ? Math.round(a.delay / 60) : 0;
      const delayStr = delay > 0 ? ` (+${delay}min)` : delay < 0 ? ` (${delay}min)` : '';
      const cancelled = a.cancelled ? ' ❌ CANCELLED' : '';
      const prov = a.provenance || a.direction || '?';
      console.log(`  ${hour}:${min}  ${a.line?.name || '?'}  von ${prov}${delayStr}${cancelled}`);
    });
  } else {
    console.log('\nNo arrivals() method available.');
  }
} catch (e) {
  console.log('Arrivals error:', e.message);
}

console.log('\n=== DEPARTURES (16:00 - 16:30) ===');
try {
  const result = await client.departures(stationId, { when, duration: 30 });
  const departures = result.departures || [];
  console.log(`Found ${departures.length} departures`);
  
  departures.forEach(d => {
    const planned = new Date(d.plannedWhen);
    const hour = planned.getHours();
    const min = planned.getMinutes().toString().padStart(2, '0');
    const delay = d.delay ? Math.round(d.delay / 60) : 0;
    const delayStr = delay > 0 ? ` (+${delay}min)` : delay < 0 ? ` (${delay}min)` : '';
    const cancelled = d.cancelled ? ' ❌ CANCELLED' : '';
    console.log(`  ${hour}:${min}  ${d.line?.name || '?'}  → ${d.direction}${delayStr}${cancelled}`);
  });
} catch (e) {
  console.log('Departures error:', e.message);
}
