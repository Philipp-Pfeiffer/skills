#!/usr/bin/env python3
"""
Autobahn API CLI tool.

Query current road conditions, roadworks, traffic warnings, closures,
webcams, parking, and charging stations for German highways.
No API key required.
"""

import argparse
import json
import os
import sys
import time
from urllib.parse import urljoin

import requests

BASE_URL = "https://verkehr.autobahn.de/o/autobahn"


def api_get(path):
    """Make a GET request to the Autobahn API."""
    url = urljoin(BASE_URL + "/", path.lstrip("/"))
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        print(f"Error fetching data: {exc}", file=sys.stderr)
        sys.exit(1)


def list_roads():
    """List all available roads."""
    data = api_get("/")
    return data.get("roads", [])


def list_roadworks(road_id):
    """List roadworks for a road."""
    data = api_get(f"/{road_id}/services/roadworks")
    return data.get("roadworks", [])


def list_warnings(road_id):
    """List traffic warnings for a road."""
    data = api_get(f"/{road_id}/services/warning")
    return data.get("warning", [])


def list_closures(road_id):
    """List closures for a road."""
    data = api_get(f"/{road_id}/services/closure")
    return data.get("closure", [])


def list_webcams(road_id):
    """List webcams for a road."""
    data = api_get(f"/{road_id}/services/webcam")
    return data.get("webcam", [])


def list_parking(road_id):
    """List parking/lorry spots for a road."""
    data = api_get(f"/{road_id}/services/parking_lorry")
    return data.get("parking_lorry", [])


def list_charging(road_id):
    """List electric charging stations for a road."""
    data = api_get(f"/{road_id}/services/electric_charging_station")
    return data.get("electric_charging_station", [])


def get_detail(endpoint, item_id):
    """Get details for a specific item."""
    return api_get(f"/details/{endpoint}/{item_id}")


def format_item(item):
    """Format a generic road item as a one-line summary."""
    title = item.get("title", "Unknown")
    subtitle = item.get("subtitle", "")
    display = item.get("display_type", "")
    blocked = item.get("isBlocked", "false")
    status = "🚫 BLOCKED" if blocked.lower() == "true" else ""

    line = f"[{display}] {title}"
    if subtitle:
        line += f" | {subtitle}"
    if status:
        line += f" {status}"

    # Add delay info for warnings
    delay = item.get("delayTimeValue")
    if delay:
        line += f" | +{delay} min"

    # Add coordinates
    point = item.get("point", "")
    if point:
        line += f" | 📍 {point}"

    return line


def format_detail(item):
    """Format full details for an item."""
    lines = []
    lines.append(f"Title:      {item.get('title', 'N/A')}")
    lines.append(f"Subtitle:   {item.get('subtitle', 'N/A')}")
    lines.append(f"Type:       {item.get('display_type', 'N/A')}")
    lines.append(f"Blocked:    {item.get('isBlocked', 'N/A')}")
    lines.append(f"Identifier: {item.get('identifier', 'N/A')}")

    point = item.get("point", "")
    if point:
        lines.append(f"Location:   {point}")

    coord = item.get("coordinate", {})
    if coord:
        lines.append(f"Coords:     lat={coord.get('lat')}, long={coord.get('long')}")

    start = item.get("startTimestamp", "")
    if start:
        lines.append(f"Started:    {start}")

    delay = item.get("delayTimeValue")
    if delay:
        lines.append(f"Delay:      +{delay} minutes")

    traffic = item.get("abnormalTrafficType")
    if traffic:
        lines.append(f"Traffic:    {traffic}")

    desc = item.get("description", [])
    if desc:
        lines.append("")
        lines.append("Description:")
        for d in desc:
            lines.append(f"  {d}")

    # Webcam-specific
    imageurl = item.get("imageurl")
    if imageurl:
        lines.append("")
        lines.append(f"Image URL:  {imageurl}")
    linkurl = item.get("linkurl")
    if linkurl:
        lines.append(f"Stream URL: {linkurl}")

    # Parking-specific
    features = item.get("lorryParkingFeatureIcons", [])
    if features:
        lines.append("")
        lines.append("Features:")
        for f in features:
            lines.append(f"  - {f.get('description', '')}")

    # Charging-specific
    op = item.get("operator")
    if op:
        lines.append(f"Operator:   {op}")

    footer = item.get("footer", [])
    if footer:
        lines.append("")
        lines.append("Footer:")
        for f in footer:
            lines.append(f"  {f}")

    return "\n".join(lines)


def download_image(url, out_dir="."):
    """Download an image from URL."""
    filename = os.path.basename(url.split("?")[0]) or "webcam.jpg"
    filepath = os.path.join(out_dir, filename)
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        print(f"Downloaded: {filepath}")
        return filepath
    except requests.RequestException as exc:
        print(f"Error downloading image: {exc}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Autobahn API CLI - German highway traffic data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s --roads
  %(prog)s A8 --roadworks
  %(prog)s A8 --warnings
  %(prog)s A8 --closures
  %(prog)s A8 --webcams
  %(prog)s A8 --parking
  %(prog)s A8 --charging
  %(prog)s A8 --all
  %(prog)s --detail warning <id>
  %(prog)s --download-image <url>
""",
    )
    parser.add_argument("road", nargs="?", help="Road identifier, e.g. A8, A1, B2")
    parser.add_argument("--roads", action="store_true", help="List all available roads")
    parser.add_argument("--roadworks", action="store_true", help="List roadworks")
    parser.add_argument("--warnings", action="store_true", help="List traffic warnings")
    parser.add_argument("--closures", action="store_true", help="List closures")
    parser.add_argument("--webcams", action="store_true", help="List webcams")
    parser.add_argument("--parking", action="store_true", help="List parking/lorry spots")
    parser.add_argument("--charging", action="store_true", help="List charging stations")
    parser.add_argument("--all", action="store_true", help="Show roadworks, warnings, closures, webcams, parking, charging")
    parser.add_argument("--detail", metavar="TYPE", help="Get details for an item type (roadworks, warning, closure, webcam, parking_lorry, electric_charging_station)")
    parser.add_argument("--id", dest="detail_id", help="Item identifier for --detail")
    parser.add_argument("--download-image", metavar="URL", help="Download webcam image")
    parser.add_argument("--output-dir", default=".", help="Output directory for downloads")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if args.download_image:
        download_image(args.download_image, args.output_dir)
        return

    if args.roads:
        roads = list_roads()
        if args.json:
            print(json.dumps(roads, indent=2))
        else:
            print("Available roads:")
            for r in roads:
                print(f"  {r}")
        return

    if args.detail:
        if not args.detail_id:
            print("--id is required with --detail", file=sys.stderr)
            sys.exit(1)
        item = get_detail(args.detail, args.detail_id)
        if args.json:
            print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            print(format_detail(item))
        return

    if not args.road:
        parser.print_help()
        sys.exit(1)

    road = args.road.upper()

    results = {}
    if args.all or args.roadworks:
        results["roadworks"] = list_roadworks(road)
    if args.all or args.warnings:
        results["warnings"] = list_warnings(road)
    if args.all or args.closures:
        results["closures"] = list_closures(road)
    if args.all or args.webcams:
        results["webcams"] = list_webcams(road)
    if args.all or args.parking:
        results["parking"] = list_parking(road)
    if args.all or args.charging:
        results["charging"] = list_charging(road)

    if not results:
        # Default: show warnings and roadworks
        results["roadworks"] = list_roadworks(road)
        results["warnings"] = list_warnings(road)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    for category, items in results.items():
        print(f"\n=== {category.upper()} ({len(items)}) ===")
        if not items:
            print("  (none)")
            continue
        for item in items:
            print(format_item(item))


if __name__ == "__main__":
    main()
