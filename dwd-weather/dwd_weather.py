#!/usr/bin/env python3
"""DWD Weather CLI — German weather forecasts and warnings via bund.dev API."""
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dwd_stations import fetch_stations, search_stations, find_nearest_station, get_station_by_id
from dwd_forecast import get_forecast, get_warnings, format_forecast, format_warnings

def cmd_forecast(args):
    station_id = args.station
    if not station_id:
        print("Error: No station ID provided.")
        sys.exit(1)
    data = get_forecast(station_id)
    print(format_forecast(data, hourly_count=args.hourly))

def cmd_warnings(args):
    wtype = args.type or "all"
    data = get_warnings(wtype)
    print(format_warnings(data, wtype))

def cmd_stations(args):
    if args.action == "search":
        results = search_stations(args.query)
        if not results:
            print(f"No stations found for '{args.query}'.")
            return
        print(f"Found {len(results)} stations (showing first 20):")
        for s in results[:20]:
            print(f"  {s['id']:8s} {s['name']:35s} {s['lat']:8.4f} {s['lon']:8.4f} {s['state']}")
    elif args.action == "nearest":
        lat, lon = args.lat, args.lon
        s = find_nearest_station(lat, lon)
        if s:
            print(f"Nearest station: {s['id']} — {s['name']} ({s['distance_km']} km away)")
            print(f"  Coordinates: {s['lat']:.4f}, {s['lon']:.4f} | Height: {s['height']}m | State: {s['state']}")
        else:
            print("No stations found.")
    elif args.action == "get":
        s = get_station_by_id(args.station_id)
        if s:
            print(f"Station {s['id']}: {s['name']}")
            print(f"  Coordinates: {s['lat']:.4f}, {s['lon']:.4f} | Height: {s['height']}m | State: {s['state']}")
            print(f"  Data range: {s['begin']} – {s['end']}")
        else:
            print(f"Station {args.station_id} not found.")
    elif args.action == "refresh":
        print("Refreshing station cache...")
        fetch_stations(force=True)
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
    p_forecast = subparsers.add_parser("forecast", help="10-day weather forecast for a station")
    p_forecast.add_argument("station", help="DWD station ID (e.g., 10865, G005)")
    p_forecast.add_argument("--hourly", type=int, default=12, help="Number of hourly entries to show (default: 12)")
    p_forecast.set_defaults(func=cmd_forecast)

    # warnings
    p_warnings = subparsers.add_parser("warnings", help="Current weather warnings")
    p_warnings.add_argument("--type", choices=["gemeinde", "nowcast", "coast", "all"], default="all",
                            help="Warning type (default: all)")
    p_warnings.set_defaults(func=cmd_warnings)

    # stations
    p_stations = subparsers.add_parser("stations", help="Search or lookup DWD stations")
    p_stations.add_argument("action", choices=["search", "nearest", "get", "refresh"],
                           help="Action to perform")
    p_stations.add_argument("query", nargs="?", help="Search query (for 'search')")
    p_stations.add_argument("--lat", type=float, help="Latitude (for 'nearest')")
    p_stations.add_argument("--lon", type=float, help="Longitude (for 'nearest')")
    p_stations.add_argument("--station-id", help="Station ID (for 'get')")
    p_stations.set_defaults(func=cmd_stations)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
