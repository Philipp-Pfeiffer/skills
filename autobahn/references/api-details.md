# Autobahn API Details

## Base URL

`https://verkehr.autobahn.de/o/autobahn`

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | List all available roads |
| `GET /{roadId}/services/roadworks` | Roadworks |
| `GET /{roadId}/services/warning` | Traffic warnings |
| `GET /{roadId}/services/closure` | Closures |
| `GET /{roadId}/services/webcam` | Webcams |
| `GET /{roadId}/services/parking_lorry` | Parking / rest stops |
| `GET /{roadId}/services/electric_charging_station` | EV charging stations |
| `GET /details/{type}/{id}` | Details for a specific item |

## Road ID Format

Any valid German road designation: `A8`, `A1`, `B2`, `S1234`, etc.

## Common Response Fields

| Field | Description |
|-------|-------------|
| `identifier` | Unique base64-encoded ID |
| `title` | Human-readable title |
| `subtitle` | Direction or additional info |
| `display_type` | Category (ROADWORKS, WARNING, CLOSURE, WEBCAM, PARKING, STRONG_ELECTRIC_CHARGING_STATION, ELECTRIC_CHARGING_STATION) |
| `isBlocked` | `"true"` or `"false"` |
| `point` | `"long,lat"` WGS84 coordinate |
| `coordinate` | Object with `lat` and `long` |
| `extent` | Bounding box `"minLong,minLat,maxLong,maxLat"` |
| `description` | Array of detail lines |
| `startTimestamp` | ISO 8601 timestamp |
| `future` | Boolean, true if planned |

## Warning-Specific Fields

| Field | Description |
|-------|-------------|
| `delayTimeValue` | Delay in minutes |
| `abnormalTrafficType` | e.g. `QUEUING_TRAFFIC`, `STATIONARY_TRAFFIC` |
| `geometry` | GeoJSON LineString of affected route |

## Webcam-Specific Fields

| Field | Description |
|-------|-------------|
| `imageurl` | Static JPEG image URL |
| `linkurl` | Live stream player URL |
| `operator` | State operator (e.g. NRW, Bayern) |

## Parking-Specific Fields

| Field | Description |
|-------|-------------|
| `lorryParkingFeatureIcons` | Array of amenity icons and descriptions |

## Charging Station-Specific Fields

| Field | Description |
|-------|-------------|
| `description` | Includes plug types and kW ratings |
