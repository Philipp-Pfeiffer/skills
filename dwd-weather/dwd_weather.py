#!/usr/bin/env python3
"""DWD Weather CLI — German weather forecasts and warnings via bund.dev API."""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dwd_stations import (
    resolve_location,
    get_station_by_id,
    search_stations,
    find_nearest_station,
    get_stations,
    clear_station_cache,
)
from dwd_forecast import get_forecast, get_warnings, format_forecast, format_warnings


def cmd_forecast(args):
    station_id = args.station
    if not station_id:
        print("Error: No station or location provided.")
        sys.exit(1)

    # Try to resolve the input — could be a station ID or a city name
    resolved = resolve_location(station_id)
    if not resolved:
        print(f"Error: Could not resolve location '{station_id}'.")
        sys.exit(1)

    actual_id = resolved["id"]
    data = get_forecast(actual_id)

    if "error" in data:
        print(f"Error: {data['error']}")
        sys.exit(1)

    # Show resolution info if it wasn't a direct ID match
    if resolved.get("matched_by") == "name":
        print(f"📍 Resolved '{station_id}' → MOSMIX station {actual_id} ({resolved['name']})")
        print()
    elif resolved.get("matched_by") == "geocode":
        dist = resolved.get("distance_km", 0)
        geo_name = resolved.get("geocoded_name", "")
        print(f"📍 Resolved '{station_id}' → {geo_name}")
        print(f"📡 Nearest MOSMIX station: {actual_id} ({resolved['name']}, {dist} km away)")
        print()

    print(format_forecast(data, hourly_count=args.hourly))


def cmd_warnings(args):
    wtype = args.type or "all"
    data = get_warnings(wtype)
    print(format_warnings(data, wtype))


def cmd_stations(args):
    if args.action == "search":
        results = search_stations(args.query)
        if not results:
            print(f"No MOSMIX stations found for '{args.query}'.")
            return
        print(f"Found {len(results)} MOSMIX stations (showing first 20):")
        for s in results[:20]:
            print(
                f"  {s['id']:8s} {s['name']:35s} {s['lat']:8.4f} {s['lon']:8.4f}"
            )
    elif args.action == "nearest":
        lat, lon = args.lat, args.lon
        s = find_nearest_station(lat, lon)
        if s:
            print(
                f"Nearest station: {s['id']} — {s['name']} ({s['distance_km']} km away)"
            )
            print(
                f"  Coordinates: {s['lat']:.4f}, {s['lon']:.4f} | Elevation: {s.get('elevation', '?')}m"
            )
        else:
            print("No stations found.")
    elif args.action == "get":
        s = get_station_by_id(args.station_id)
        if s:
            print(f"Station {s['id']}: {s['name']}")
            print(
                f"  Coordinates: {s['lat']:.4f}, {s['lon']:.4f} | Elevation: {s.get('elevation', '?')}m"
            )
        else:
            print(f"Station {args.station_id} not found.")
    elif args.action == "resolve":
        if not args.query:
            print("Error: --query required for resolve")
            sys.exit(1)
        r = resolve_location(args.query)
        if r:
            matched = r.get("matched_by", "?")
            extra = ""
            if matched == "geocode":
                extra = f" (geocoded '{r.get('geocoded_name')}')"
            print(
                f"Resolved '{args.query}' → {r['id']} {r['name']} [{matched}]{extra}"
            )
        else:
            print(f"Could not resolve: {args.query}")
    elif args.action == "refresh":
        print("Clearing station resolution cache...")
        clear_station_cache()
        print("Done.")
    else:
        print(f"Unknown action: {args.action}")


def main():
    parser = argparse.ArgumentParser(
        prog="dwd-weather",
        description="DWD Weather CLI — forecasts and warnings for Germany via bund.dev API",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # forecast
    p_forecast = subparsers.add_parser(
        "forecast", help="10-day weather forecast for a station or city"
    )
    p_forecast.add_argument(
        "station",
        help="City name or MOSMIX station ID (e.g., 10865, G005, Karlsruhe, Berlin)",
    )
    p_forecast.add_argument(
        "--hourly",
        type=int,
        default=12,
        help="Number of hourly entries to show (default: 12)",
    )
    p_forecast.set_defaults(func=cmd_forecast)

    # warnings
    p_warnings = subparsers.add_parser("warnings", help="Current weather warnings")
    p_warnings.add_argument(
        "--type",
        choices=["gemeinde", "nowcast", "coast", "all"],
        default="all",
        help="Warning type (default: all)",
    )
    p_warnings.set_defaults(func=cmd_warnings)

    # stations
    p_stations = subparsers.add_parser(
        "stations", help="Search or lookup MOSMIX stations"
    )
    p_stations.add_argument(
        "action",
        choices=["search", "nearest", "get", "resolve", "refresh"],
        help="Action to perform",
    )
    p_stations.add_argument("query", nargs="?", help="Search query (for 'search', 'resolve')")
    p_stations.add_argument("--lat", type=float, help="Latitude (for 'nearest')")
    p_stations.add_argument("--lon", type=float, help="Longitude (for 'nearest')")
    p_stations.add_argument("--station-id", help="Station ID (for 'get')")
    p_stations.set_defaults(func=cmd_stations)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
