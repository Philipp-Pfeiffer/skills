# Common Deutsche Bahn Station IDs

## Quick Reference - Major German Stations

| Station Name | Station ID |
|--------------|------------|
| Berlin Hbf | 8098160 |
| München Hbf | 8000261 |
| Frankfurt (Main) Hbf | 8000105 |
| Hamburg Hbf | 8002549 |
| Köln Hbf | 8000207 |
| Dortmund Hbf | 8000080 |
| Leipzig Hbf | 8010202 |
| Stuttgart Hbf | 8000096 |
| München Hbf | 8000261 |
| Ulm Hbf | 8000227 |
| Frankfurt (Main) Flughafen | 8000051 |
| Düsseldorf Hbf | 8000085 |
| Hannover Hbf | 8000152 |
| Nürnberg Hbf | 8000284 |
| Bremen Hbf | 8000045 |

## How to Find Station IDs

Use the `locations()` method to search for stations:

```javascript
import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

const client = createClient(dbnavProfile, 'my-user-agent');

const stations = await client.locations('Stuttgart');
stations.forEach(s => {
  console.log(`${s.name} (ID: ${s.id}, type: ${s.type})`);
});
```

**Output:**
```
Stuttgart Hbf (ID: 8000096, type: station)
Stuttgart (ID: 8000096, type: station)
Stuttgart-Bad Cannstatt (ID: 8000074, type: station)
...
```

## Station ID Format

Deutsche Bahn station IDs follow the format:
- 7-digit number
- Usually starts with 80
- Unique identifier for each station

## Notes

- Station IDs are stable and don't change
- The `type` field is usually 'station' for train stations
- Some locations may have `id: null` if they're addresses or POIs rather than stations
- Always use the numeric ID, not the name, for API calls to ensure accuracy
