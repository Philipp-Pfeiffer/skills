# Deutsche Bahn Vendo API Reference

## Overview

Deutsche Bahn has migrated from the old HAFAS API to the new **Vendo/Movas** platform. The `db-vendo-client` npm package provides a JavaScript client for these new APIs.

## Installation

```bash
npm install db-vendo-client
```

## Quick Start

```javascript
import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

const client = createClient(dbnavProfile, 'my-user-agent');

// Get departures with real-time delays
const { departures } = await client.departures('8000261', { // München Hbf
  when: new Date(),
  duration: 60,
  remarks: true
});

departures.forEach(dep => {
  console.log(`${dep.line.name}: ${dep.delay} seconds delay`);
});
```

## API Profiles

The `db-vendo-client` supports four different profiles with varying capabilities:

| Profile | API Key Required | Stability | Rate Limit | Duration | Remarks | Best For |
|---------|-----------------|-----------|------------|----------|---------|----------|
| **dbnav** | No | More stable | Aggressive blocking | 1h | Most important only | DB Navigator app |
| **db** | No | Less stable | 60/min (IPv4) | 1h | Most important only | General use |
| **dbweb** | No | Less stable | Aggressive blocking | 1h | All remarks | bahn.de |
| **dbris** | **Yes** | Most stable | Depends on key | 12h | All remarks | Production use |

**Recommended profile**: `dbnav` for most use cases. Use `dbris` for production with API key.

## Key Endpoints

### departures(stationId, options)

Get upcoming departures from a station with real-time delay information.

**Parameters:**
- `stationId`: Station ID (e.g., '8000261' for München Hbf)
- `options.when`: Date object for when to search
- `options.duration`: Minutes to search ahead (default varies by profile)
- `options.remarks`: Boolean to include disruption info

**Returns:**
```javascript
{
  departures: [
    {
      line: { name: 'ICE 801', id: '...' },
      direction: 'München Hbf',
      plannedWhen: Date,     // Scheduled departure time
      when: Date,            // Actual/prognosed departure time
      delay: 120,            // Delay in seconds (null if on time)
      cancelled: false,      // True if cancelled
      plannedPlatform: '1',
      platform: '2',         // Platform change if different
      remarks: [             // Disruption info
        { type: 'warning', text: 'Construction work' }
      ]
    }
  ]
}
```

### journeys(from, to, options)

Get route connections between two stations.

**Parameters:**
- `from`: `{ type: 'station', id: '...' }`
- `to`: `{ type: 'station', id: '...' }`
- `options.results`: Number of connections to return

**Note:** Does NOT include real-time delay data. Use `departures()` for delays.

### locations(query, options)

Search for stations by name.

```javascript
const stations = await client.locations('München');
// Returns: [{ id: '8000261', name: 'München Hbf', type: 'station' }, ...]
```

## Delay Data Fields

When checking delays, use these fields:

- **`plannedWhen`**: Scheduled departure time
- **`when`**: Actual/prognosed departure time
- **`delay`**: Delay in seconds (null if on time)
- **`cancelled`**: True if service is cancelled
- **`platform`**: Current platform (may differ from `plannedPlatform`)
- **`remarks`**: Array of disruption/delay information

**Example:**
```javascript
const delayMinutes = dep.delay ? Math.round(dep.delay / 60) : 0;
const status = dep.cancelled ? 'CANCELLED' :
               delayMinutes === 0 ? 'On time' :
               `${delayMinutes} min delay`;
```

## Common Station IDs

| Station | ID |
|---------|-----|
| Berlin Hbf | 8098160 |
| München Hbf | 8000261 |
| Frankfurt (Main) Hbf | 8000105 |
| Hamburg Hbf | 8002549 |
| Köln Hbf | 8000207 |
| Frankfurt (Main) Flughafen | 8000051 |

## Limitations

Compared to the old HAFAS API, Vendo has some limitations:

- No `tripsByName()`, `radar()`, `journeysFromTrip()`, `reachableFrom()`, `remarks()`, `lines()`, `station()` endpoints
- No load factor data in departure boards
- Some query options/filters not available (e.g., routingMode for journeys)
- `journeys()` does NOT include real-time delays - use `departures()` instead

## Important Notes

1. **Real-time delays only available via `departures()`** - The `journeys()` endpoint provides planned schedules but not real-time delays.

2. **Respect rate limits** - Use caching or the `cached-hafas-client` wrapper to avoid hitting limits.

3. **User agent required** - Always provide a user agent string when creating the client.

4. **Delay in seconds** - The `delay` field is in seconds, not minutes. Convert: `delay / 60`.

5. **Null delay means on time** - `delay: null` means the service is running on time, not that delay data is unavailable.

## Further Reading

- GitHub: https://github.com/public-transport/db-vendo-client
- NPM: https://www.npmjs.com/package/db-vendo-client
- DB API documentation: See `docs/db-apis.md` in the repository
