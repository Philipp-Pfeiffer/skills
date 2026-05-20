#!/usr/bin/env python3
"""
FBI Wanted API CLI tool.

Fetch and filter wanted persons from the FBI Wanted API.
No API key required.
"""

import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlencode

import requests

BASE_URL = "https://api.fbi.gov/wanted/v1/list"
PAGE_SIZE = 20


def fetch_page(page=1, field_offices=None, subjects=None, delay=0.5):
    """Fetch a single page from the FBI Wanted API with retry on 429."""
    params = {"page": page}
    if field_offices:
        params["field_offices"] = field_offices
    if subjects:
        params["subjects"] = subjects

    url = f"{BASE_URL}?{urlencode(params)}"
    max_retries = 5
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 429:
                wait = (2 ** attempt) + 0.5
                print(f"Rate limited (429). Retrying in {wait:.1f}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            if delay:
                time.sleep(delay)
            return resp.json()
        except requests.RequestException as exc:
            print(f"Error fetching data: {exc}", file=sys.stderr)
            sys.exit(1)
    print("Rate limited. Max retries exceeded.", file=sys.stderr)
    sys.exit(1)


def fetch_all(field_offices=None, subjects=None, delay=0.5):
    """Fetch all pages from the FBI Wanted API."""
    all_items = []
    page = 1
    while True:
        data = fetch_page(page, field_offices, subjects, delay=delay)
        items = data.get("items", [])
        if not items:
            break
        all_items.extend(items)
        total = data.get("total", 0)
        if page * PAGE_SIZE >= total:
            break
        page += 1
    return all_items


def parse_reward(reward_text):
    """Extract numeric reward value from reward_text string."""
    if not reward_text:
        return 0
    match = re.search(r"[\$€£]?\s*([\d,]+)", reward_text)
    if match:
        return int(match.group(1).replace(",", ""))
    return 0


def filter_by_name(items, query):
    """Filter items by name (case-insensitive)."""
    query = query.lower()
    return [item for item in items if query in item.get("title", "").lower()]


def filter_by_reward(items, min_reward):
    """Filter items by minimum reward amount."""
    return [item for item in items if parse_reward(item.get("reward_text")) >= min_reward]


def filter_status(items, status):
    """Filter items by status."""
    return [item for item in items if item.get("status", "").lower() == status.lower()]


def filter_by_subjects(items, subject):
    """Filter items by subjects (client-side fallback)."""
    subject_lower = subject.lower()
    return [
        item for item in items
        if any(subject_lower in s.lower() for s in item.get("subjects", []))
    ]


def format_summary(item):
    """Return a one-line summary for an item."""
    title = item.get("title", "Unknown")
    status = item.get("status", "na")
    reward = item.get("reward_text", "")
    subjects = ", ".join(item.get("subjects", [])[:2])
    uid = item.get("uid", "")
    line = f"{title} | Status: {status}"
    if reward:
        line += f" | Reward: {reward}"
    if subjects:
        line += f" | {subjects}"
    line += f" | UID: {uid}"
    return line


def format_detail(item):
    """Return a detailed view for an item."""
    lines = []
    lines.append(f"Title:        {item.get('title', 'N/A')}")
    lines.append(f"UID:          {item.get('uid', 'N/A')}")
    lines.append(f"Status:       {item.get('status', 'na')}")
    lines.append(f"Description:  {item.get('description', 'N/A')}")
    lines.append(f"Subjects:     {', '.join(item.get('subjects', []))}")
    lines.append(f"Reward:       {item.get('reward_text', 'N/A')}")
    lines.append(f"Dates of Birth Used: {', '.join(item.get('dates_of_birth_used', []))}")
    lines.append(f"Place of Birth: {item.get('place_of_birth', 'N/A')}")
    lines.append(f"Hair:         {item.get('hair', 'N/A')}")
    lines.append(f"Eyes:         {item.get('eyes', 'N/A')}")
    lines.append(f"Height:       {item.get('height', 'N/A')}")
    lines.append(f"Weight:       {item.get('weight', 'N/A')}")
    lines.append(f"Sex:          {item.get('sex', 'N/A')}")
    lines.append(f"Race:         {item.get('race', 'N/A')}")
    lines.append(f"Nationality:  {item.get('nationality', 'N/A')}")
    lines.append(f"Scars and Marks: {item.get('scars_and_marks', 'N/A')}")
    lines.append(f"NCIC:         {item.get('ncic', 'N/A')}")
    lines.append(f"Field Offices: {', '.join(item.get('field_offices', []))}")
    lines.append(f"Caution:      {item.get('caution', 'N/A')}")

    images = item.get("images", [])
    if images:
        lines.append(f"Images:")
        for img in images:
            lines.append(f"  - {img.get('large', img.get('original', 'N/A'))}")

    files = item.get("files", [])
    if files:
        lines.append(f"Files:")
        for f in files:
            lines.append(f"  - {f.get('url', 'N/A')} ({f.get('name', 'file')})")

    return "\n".join(lines)


def download_image(url, out_dir="."):
    """Download an image from URL to out_dir."""
    filename = os.path.basename(url.split("?")[0]) or "image.jpg"
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
        description="FBI Wanted API CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  %(prog)s --list
  %(prog)s --list --category "Violent Crime - Murders"
  %(prog)s --list --office newark
  %(prog)s --search "Bob Tang"
  %(prog)s --details <uid>
  %(prog)s --top
  %(prog)s --reward-min 10000
  %(prog)s --download-image <image_url>
""",
    )
    parser.add_argument("--list", action="store_true", help="List wanted persons (default: first page)")
    parser.add_argument("--all", action="store_true", help="Fetch all pages (may be slow)")
    parser.add_argument("--category", metavar="SUBJECT", help="Filter by subject/category")
    parser.add_argument("--office", metavar="OFFICE", help="Filter by FBI field office")
    parser.add_argument("--search", metavar="NAME", help="Search by name (client-side)")
    parser.add_argument("--details", metavar="UID", help="Show details for a specific UID")
    parser.add_argument("--top", action="store_true", help="Show Top Ten Most Wanted")
    parser.add_argument("--reward-min", type=int, metavar="AMOUNT", help="Filter by minimum reward")
    parser.add_argument("--status", metavar="STATUS", help="Filter by status (na, captured, etc.)")
    parser.add_argument("--download-image", metavar="URL", help="Download image from URL")
    parser.add_argument("--output-dir", default=".", help="Output directory for downloads")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of results")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between API requests in seconds (default: 0.5)")

    args = parser.parse_args()

    if args.download_image:
        download_image(args.download_image, args.output_dir)
        return

    if args.details:
        items = fetch_all(field_offices=args.office, subjects=args.category)
        for item in items:
            if item.get("uid") == args.details:
                if args.json:
                    print(json.dumps(item, indent=2))
                else:
                    print(format_detail(item))
                return
        print(f"UID '{args.details}' not found.", file=sys.stderr)
        sys.exit(1)

    if args.top:
        args.category = "Ten Most Wanted Fugitives"
        args.all = True

    if args.all or args.search or args.reward_min or args.status or args.top:
        items = fetch_all(field_offices=args.office, subjects=args.category, delay=args.delay)
    else:
        data = fetch_page(page=1, field_offices=args.office, subjects=args.category, delay=args.delay)
        items = data.get("items", [])

    # Client-side subject filter (API sometimes ignores subjects param)
    if args.category:
        items = filter_by_subjects(items, args.category)

    if args.search:
        items = filter_by_name(items, args.search)

    if args.reward_min:
        items = filter_by_reward(items, args.reward_min)

    if args.status:
        items = filter_status(items, args.status)

    if args.limit:
        items = items[:args.limit]

    if args.json:
        print(json.dumps(items, indent=2))
    else:
        if not items:
            print("No results found.")
        else:
            print(f"Results: {len(items)}")
            print("-" * 60)
            for item in items:
                print(format_summary(item))


if __name__ == "__main__":
    main()
