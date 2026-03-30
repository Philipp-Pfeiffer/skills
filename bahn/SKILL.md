---
name: bahn
description: Check Deutsche Bahn train connections, real-time delays, ticket prices, and Bahncard discounts. Use when users need to check if their train or bus is on time, find connections between stations, get departure boards with delay information, look up station IDs, check ticket prices, or compare Bahncard savings. Supports db-vendo-client with real-time delay data, pricing, and loyalty card integration from German public transport.
---

# Bahn Delays

Check Deutsche Bahn train connections and real-time delay information using the db-vendo-client API.

## Quick Start

**To check if a train is on time:**

```javascript
import { createClient } from 'db-vendo-client';
import { profile as dbnavProfile } from 'db-vendo-client/p/dbnav/index.js';

const client = createClient(dbnavProfile, 'user-agent');
const { departures } = await client.departures('8098160', { // Berlin Hbf
  when: new Date(),
  duration: 60
});

departures.forEach(dep => {
  const delay = dep.delay ? Math.round(dep.delay / 60) : 0;
  console.log(`${dep.line.name}: ${delay} min delay`);
});
```

**To find connections:**

Use the bundled `scripts/check-route.mjs` script or the `journeys()` endpoint. See [API Reference](references/api-reference.md) for details.

## Common Tasks

### 1. Check Delays at a Station

Use the `scripts/check-delays.mjs` script to check upcoming departures:

```bash
node scripts/check-delays.mjs
```

Edit the script to change the station ID or duration.

### 2. Check Specific Route

Use `scripts/check-route.mjs` to check connections between two stations:

```bash
node scripts/check-route.mjs
```

### 3. Find Station ID

Use the `locations()` method:

```javascript
const stations = await client.locations('München');
console.log(stations[0].id); // e.g., 8000261 for München Hbf
```

See [Station IDs](references/station-ids.md) for common stations.

### 4. Check Ticket Prices

Use `scripts/check-price.mjs` to check ticket prices for routes:

```bash
node scripts/check-price.mjs
```

Or use the `journeys()` endpoint:

```javascript
const { journeys } = await client.journeys(fromId, toId, {
  departure: new Date(),
  results: 3
});

journeys.forEach(j => {
  if (j.price) {
    console.log(`Price: ${j.price.amount} ${j.price.currency}`);
  }
});
```

**With Bahncard discounts:**

The skill supports Bahncard pricing. Specify loyalty card for discounted prices:

```javascript
import { data as cards } from 'db-vendo-client/format/loyalty-cards.js';

const { journeys } = await client.journeys(fromId, toId, {
  departure: new Date(),
  results: 3,
  loyaltyCard: {
    type: cards.BAHNCARD,
    discount: 25,  // or 50
    class: 2       // 1st or 2nd class
  }
});
```

**Note:** Pricing is returned in EUR and may vary based on time, train type, Bahncard status, and availability.

### 5. Get Departure Board with Real-Time Data

```javascript
const { departures } = await client.departures(stationId, {
  when: new Date(),
  duration: 60,
  remarks: true
});

departures.forEach(dep => {
  console.log(`${dep.line.name} to ${dep.direction}`);
  console.log(`Planned: ${dep.plannedWhen}`);
  console.log(`Actual: ${dep.when}`);
  console.log(`Delay: ${dep.delay ? Math.round(dep.delay/60) + ' min' : 'On time'}`);

  if (dep.cancelled) {
    console.log('⚠️ CANCELLED');
  }

  if (dep.remarks?.length > 0) {
    console.log(`Remarks: ${dep.remarks.length}`);
  }
});
```

## Important Notes

1. **Use `departures()` for delays** - The `journeys()` endpoint does NOT include real-time delays. Only `departures()` provides delay data.

2. **Delay is in seconds** - Convert to minutes: `Math.round(dep.delay / 60)`

3. **`null` delay means on time** - Not missing data

4. **Choose the right profile** - See [API Reference](references/api-reference.md#api-profiles) for profile comparison (dbnav recommended for most use cases)

5. **Respect rate limits** - Use caching to avoid blocking

## Understanding Delay Data

Each departure object contains:

- `plannedWhen` - Scheduled departure time
- `when` - Actual/prognosed departure time
- `delay` - Delay in seconds (null if on time)
- `cancelled` - True if service is cancelled
- `platform` - Current platform (may differ from `plannedPlatform`)
- `remarks` - Array of disruption information

## Resources

### scripts/

- **check-delays.mjs** - Check upcoming departures with delay info for any station
- **check-route.mjs** - Check connections between two specific stations

### references/

- **api-reference.md** - Complete db-vendo-client API documentation with examples
- **station-ids.md** - Common Deutsche Bahn station IDs
- **bahn-schedule.md** - Example schedule output with Vendo API info

## Troubleshooting

**No delay data returned?**
- Real-time delays may only be available closer to departure time
- Some smaller stations may have limited real-time data
- Try testing with a major station like Stuttgart Hbf (8000096)

**Rate limit errors?**
- Add delays between requests
- Use caching (consider `cached-hafas-client` wrapper)
- Try a different profile (dbnav is more stable than db/dbweb)

**Station not found?**
- Use `locations()` to search for the station name and get the correct ID
- Check if you're using the 7-digit station ID, not the name
