import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

const client = createClient(dbnavProfile, 'clawdbot');
const when = new Date('2026-04-02T11:00:00+02:00');

const { journeys } = await client.journeys('8000191', '8000096', {
  departure: when,
  results: 6
});

for (const [i, j] of journeys.entries()) {
  const dep = j.legs[0];
  const arr = j.legs[j.legs.length - 1];
  const dur = Math.round(j.duration / 60000);
  const lines = j.legs.filter(l => !l.walking).map(l => l.line?.name || '?').join(' → ');
  const transfers = j.legs.filter(l => !l.walking).length - 1;
  const xferStr = transfers > 0 ? `[${transfers} Umst.]` : '[direkt]';
  const fmtD = dep.plannedWhen || dep.departure;
  const fmtA = arr.plannedWhen || arr.arrival;
  const dStr = fmtD ? new Date(fmtD).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) : '??:??';
  const aStr = fmtA ? new Date(fmtA).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }) : '??:??';
  console.log(`${i + 1}. Ab ${dStr} → An ${aStr} (${dur} min) | ${lines} ${xferStr}`);
  if (j.price) console.log(`   ${j.price.amount} EUR`);
  console.log();
}
