import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';

async function checkJourneys() {
  const client = createClient(dbProfile, 'clawdbot-bahn-skill');

  const { journeys } = await client.journeys('8000191', '8000096', {
    departure: new Date(),
    results: 6
  });

  if (!journeys || journeys.length === 0) {
    console.log('Keine Verbindungen gefunden.');
    return;
  }

  journeys.forEach((j, i) => {
    const dep = j.legs[0];
    const arr = j.legs[j.legs.length - 1];
    const depTime = new Date(dep.plannedDeparture).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' });
    const arrTime = new Date(arr.plannedArrival).toLocaleString('de-DE', { hour: '2-digit', minute: '2-digit' });
    const depDate = new Date(dep.plannedDeparture);
    const arrDate = new Date(arr.plannedArrival);
    const durationMin = Math.round((arrDate - depDate) / 60000);

    const transitLegs = j.legs.filter(l => l.line);
    const changes = transitLegs.length - 1;

    let lineNames = transitLegs.map(l => l.line?.name || l.line?.id || '?');
    const lines = lineNames.join(' → ');

    let out = `${depTime}–${arrTime} (${durationMin} min)`;
    if (changes > 0) {
      out += `, ${changes}x Umstieg`;
    } else {
      out += `, direkt`;
    }
    out += ` — ${lines}`;
    console.log(out);
  });
}

checkJourneys().catch(console.error);
