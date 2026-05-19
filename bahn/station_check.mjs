import { createClient } from 'db-vendo-client';
import { profile as dbProfile } from 'db-vendo-client/p/db/index.js';

const client = createClient(dbProfile, 'openclaw-bahn-check');

const stations = await client.locations('Stuttgart Bad Cannstatt', { results: 5 });
console.log('Stuttgart Bad Cannstatt results:');
stations.forEach(s => console.log(`  ${s.name} | ID: ${s.id} | Type: ${s.type}`));

const stuttgart = await client.locations('Stuttgart', { results: 5 });
console.log('\nStuttgart results:');
stuttgart.forEach(s => console.log(`  ${s.name} | ID: ${s.id} | Type: ${s.type}`));
