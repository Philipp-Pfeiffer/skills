#!/usr/bin/env python3
"""
Robust iCal parser with RRULE expansion - standard library only.
Handles VEVENT extraction, recurring events, timezone-aware datetimes.
"""
import sys, re, json, urllib.request, urllib.error, os
from datetime import datetime, timedelta, date

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
DEFAULT_ICAL_URL = "https://campus.kit.edu/sp/webcal/KtLyqt0HLK"

# ------------------------------------------------------------------
# iCal line unfolding (RFC 5545)
# ------------------------------------------------------------------
def unfold_lines(raw: str) -> list:
    lines = raw.splitlines()
    out = []
    for line in lines:
        if line.startswith(" ") or line.startswith("\t"):
            if out:
                out[-1] += line[1:]
        else:
            out.append(line)
    return out

# ------------------------------------------------------------------
# Parse iCal datetime strings
# ------------------------------------------------------------------
def parse_ical_datetime(s: str, default_tz: str = "Europe/Berlin"):
    """Parse strings like 20260428T080000 or 20260428T080000Z."""
    s = s.strip()
    if ":" in s:
        s = s.split(":", 1)[1]
    tz = default_tz
    if "Z" in s:
        tz = "UTC"
    if "T" in s:
        clean = s.rstrip("Z")
        try:
            dt = datetime.strptime(clean, "%Y%m%dT%H%M%S")
        except ValueError:
            return None, tz
        return dt, tz
    else:
        try:
            dt = datetime.strptime(s, "%Y%m%d")
        except ValueError:
            return None, tz
        return dt, tz

def parse_ical_dateonly(s: str):
    """Parse date-only string 20260428."""
    s = s.strip()
    if ":" in s:
        s = s.split(":", 1)[1]
    try:
        return datetime.strptime(s, "%Y%m%d").date()
    except ValueError:
        return None

# ------------------------------------------------------------------
# Parse RRULE
# ------------------------------------------------------------------
def parse_rrule(rrule_str: str):
    """Parse RRULE string into dict."""
    result = {"freq": None, "until": None, "count": None, "interval": 1, "byday": None}
    parts = rrule_str.split(";")
    for part in parts:
        if "=" not in part:
            continue
        key, val = part.split("=", 1)
        key = key.upper()
        if key == "FREQ":
            result["freq"] = val.upper()
        elif key == "UNTIL":
            if "T" in val:
                result["until"] = datetime.strptime(val, "%Y%m%dT%H%M%S")
            else:
                result["until"] = datetime.strptime(val, "%Y%m%d")
        elif key == "COUNT":
            try:
                result["count"] = int(val)
            except ValueError:
                pass
        elif key == "INTERVAL":
            try:
                result["interval"] = int(val)
            except ValueError:
                pass
        elif key == "BYDAY":
            result["byday"] = val.upper().split(",")
    return result

# ------------------------------------------------------------------
# Day name mapping
# ------------------------------------------------------------------
DAY_MAP = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}

def day_name_to_num(d: str):
    # Remove possible numeric prefix like -1SU, 2MO
    for prefix in ["-1", "-2", "-3", "-4", "1", "2", "3", "4", "5"]:
        if d.startswith(prefix):
            d = d[len(prefix):]
            break
    return DAY_MAP.get(d)

# ------------------------------------------------------------------
# Expand recurring events
# ------------------------------------------------------------------
def expand_recurring(event, exdates=None, target_start=None, target_end=None):
    """Expand a recurring event into individual occurrences."""
    if exdates is None:
        exdates = set()

    rrule_str = event.get("RRULE")
    if not rrule_str:
        # Non-recurring: yield as-is if in range
        if target_start and target_end:
            if target_start <= event["start"].date() <= target_end:
                return [event]
            return []
        return [event]

    rrule = parse_rrule(rrule_str)
    if rrule["freq"] not in ("DAILY", "WEEKLY"):
        # Not supported: fallback to original event
        if target_start and target_end:
            if target_start <= event["start"].date() <= target_end:
                return [event]
            return []
        return [event]

    start_dt = event["start"]
    end_dt = event["end"]
    duration = end_dt - start_dt

    # Determine expansion range
    if target_start and target_end:
        range_start = datetime.combine(target_start, start_dt.time())
        range_end = datetime.combine(target_end, start_dt.time())
    else:
        range_start = start_dt
        range_end = rrule.get("until") or (start_dt + timedelta(days=365))

    occurrences = []
    current = start_dt
    count = 0
    max_count = rrule.get("count") or 9999
    until = rrule.get("until")
    interval = rrule.get("interval") or 1
    byday = rrule.get("byday")

    # If BYDAY specified, compute valid weekdays
    valid_weekdays = None
    if byday:
        valid_weekdays = [day_name_to_num(d) for d in byday if day_name_to_num(d) is not None]

    while count < max_count:
        if until and current > until:
            break
        if current > range_end:
            break

        # Check if this occurrence is excluded
        current_date = current.date()
        if current_date in exdates:
            current = _advance(current, rrule["freq"], interval)
            continue

        # Check weekday filter
        if valid_weekdays is not None:
            if current_date.weekday() not in valid_weekdays:
                current = _advance(current, rrule["freq"], interval)
                continue

        # Check range
        if current_date >= range_start.date():
            occ = dict(event)
            occ["start"] = current
            occ["end"] = current + duration
            occ["_recurring"] = True
            occurrences.append(occ)

        count += 1
        current = _advance(current, rrule["freq"], interval)

    return occurrences

def _advance(dt: datetime, freq: str, interval: int):
    if freq == "DAILY":
        return dt + timedelta(days=interval)
    elif freq == "WEEKLY":
        return dt + timedelta(weeks=interval)
    return dt + timedelta(days=interval)

# ------------------------------------------------------------------
# Extract VEVENT blocks
# ------------------------------------------------------------------
def parse_events(raw: str):
    lines = unfold_lines(raw)
    events = []
    current = {}
    in_event = False

    for line in lines:
        line = line.strip()
        if line == "BEGIN:VEVENT":
            in_event = True
            current = {}
            continue
        if line == "END:VEVENT":
            in_event = False
            if current:
                events.append(current)
            continue
        if not in_event:
            continue

        if ":" in line:
            # Handle params like DTSTART;TZID=Europe/Berlin:20251028T094500
            colon_idx = line.index(":")
            key_part = line[:colon_idx]
            val = line[colon_idx+1:]

            key_base = key_part.split(";")[0]

            if key_base == "DESCRIPTION":
                current[key_base] = current.get(key_base, "") + val
            else:
                if key_base not in current or key_base in ("DTSTART", "DTEND"):
                    current[key_part] = val

    # Normalize events + expand recurring
    out = []
    for ev in events:
        start = None
        end = None
        tz = "Europe/Berlin"

        for k, v in ev.items():
            if k.startswith("DTSTART"):
                start, tz_found = parse_ical_datetime(k + ":" + v, tz)
                if tz_found:
                    tz = tz_found
            if k.startswith("DTEND"):
                end, _ = parse_ical_datetime(k + ":" + v, tz)

        if not start or not end:
            continue

        summary = ev.get("SUMMARY", "").strip()
        location = ev.get("LOCATION", "").strip()
        description = ev.get("DESCRIPTION", "").strip()
        uid = ev.get("UID", "").strip()
        rrule = ev.get("RRULE")

        # Parse EXDATEs
        exdates = set()
        for k, v in ev.items():
            if k.startswith("EXDATE"):
                # Can be comma-separated
                for part in v.split(","):
                    d = parse_ical_dateonly(part)
                    if d:
                        exdates.add(d)

        base_event = {
            "uid": uid,
            "summary": summary,
            "location": location,
            "description": description,
            "start": start,
            "end": end,
            "tz": tz,
            "RRULE": rrule,
        }

        # Store for later expansion (we expand on demand)
        out.append((base_event, exdates))

    return out

# ------------------------------------------------------------------
# Filtering helpers (operate on expanded events)
# ------------------------------------------------------------------
def get_expanded_events(parsed_events, target_start: date = None, target_end: date = None):
    """Expand all recurring events and filter by date range."""
    all_events = []
    for base_event, exdates in parsed_events:
        expanded = expand_recurring(base_event, exdates, target_start, target_end)
        all_events.extend(expanded)
    all_events.sort(key=lambda x: x["start"])
    return all_events

def events_for_date(events, target_date: date):
    return [e for e in events if e["start"].date() == target_date]

def events_in_range(events, start_date: date, end_date: date):
    return [e for e in events if start_date <= e["start"].date() <= end_date]

def exams(events):
    keywords = ["klausur", "prüfung", "exam", "test", "mündlich", "zwischenklausur"]
    out = []
    for e in events:
        text = (e["summary"] + " " + e["description"]).lower()
        if any(k in text for k in keywords):
            out.append(e)
    return sorted(out, key=lambda x: x["start"])

# ------------------------------------------------------------------
# Formatting
# ------------------------------------------------------------------
def fmt_time(dt: datetime):
    return dt.strftime("%H:%M")

def fmt_date(dt: datetime):
    return dt.strftime("%A, %d.%m.%Y")

def event_to_line(e):
    start = fmt_time(e["start"])
    end = fmt_time(e["end"])
    line = f"{start}-{end}: {e['summary']}"
    if e["location"]:
        line += f" @ {e['location']}"
    return line

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse iCal and output schedule info")
    parser.add_argument("--url", default=os.environ.get("ICAL_URL", DEFAULT_ICAL_URL))
    parser.add_argument("--file", help="Read from .ics file instead of URL")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--today", action="store_true", help="Show today's events")
    parser.add_argument("--tomorrow", action="store_true", help="Show tomorrow's events")
    parser.add_argument("--week", action="store_true", help="Show this week's events")
    parser.add_argument("--exams", action="store_true", help="Show all exams")
    parser.add_argument("--date", help="Show events for YYYY-MM-DD")
    parser.add_argument("--next-exam", action="store_true", help="Show next upcoming exam")
    parser.add_argument("--raw", action="store_true", help="Dump raw parsed events as JSON")
    parser.add_argument("--expand-range-days", type=int, default=365, help="Days to expand recurring events")
    args = parser.parse_args()

    # Fetch
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Fetch error: {e}", file=sys.stderr)
            sys.exit(1)

    parsed_events = parse_events(raw)

    # Determine date range for expansion
    now = datetime.now()
    today = now.date()

    if args.today:
        target_start = today
        target_end = today
    elif args.tomorrow:
        target_start = today + timedelta(days=1)
        target_end = target_start
    elif args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d").date()
        target_start = d
        target_end = d
    elif args.week:
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        target_start = monday
        target_end = sunday
    elif args.exams or args.next_exam:
        target_start = today
        target_end = today + timedelta(days=args.expand_range_days)
    else:
        target_start = today
        target_end = today

    # Expand all recurring events for the target range
    events = get_expanded_events(parsed_events, target_start, target_end)

    if args.raw:
        serializable = []
        for e in events:
            serializable.append({
                "uid": e["uid"],
                "summary": e["summary"],
                "location": e["location"],
                "description": e["description"],
                "start": e["start"].isoformat(),
                "end": e["end"].isoformat(),
                "tz": e["tz"],
                "recurring": e.get("_recurring", False),
            })
        print(json.dumps(serializable, indent=2, ensure_ascii=False))
        return

    # Filter for specific query
    selected = events
    header = ""

    if args.today:
        selected = events_for_date(events, today)
        header = f"Heute - {fmt_date(datetime.combine(today, datetime.min.time()))}"
    elif args.tomorrow:
        tomorrow = today + timedelta(days=1)
        selected = events_for_date(events, tomorrow)
        header = f"Morgen - {fmt_date(datetime.combine(tomorrow, datetime.min.time()))}"
    elif args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d").date()
        selected = events_for_date(events, d)
        header = fmt_date(datetime.combine(d, datetime.min.time()))
    elif args.week:
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        selected = events_in_range(events, monday, sunday)
        header = f"Woche {monday.strftime('%d.%m')} - {sunday.strftime('%d.%m.%Y')}"
    elif args.exams:
        selected = exams(events)
        header = "Klausuren & Prüfungen"
    elif args.next_exam:
        upcoming = [e for e in exams(events) if e["start"] >= now]
        selected = upcoming[:1]
        header = "Nächste Prüfung"
    else:
        selected = events_for_date(events, today)
        header = f"Heute - {fmt_date(datetime.combine(today, datetime.min.time()))}"

    if args.json:
        serializable = []
        for e in selected:
            serializable.append({
                "uid": e["uid"],
                "summary": e["summary"],
                "location": e["location"],
                "description": e["description"],
                "start": e["start"].isoformat(),
                "end": e["end"].isoformat(),
                "tz": e["tz"],
                "recurring": e.get("_recurring", False),
            })
        print(json.dumps(serializable, indent=2, ensure_ascii=False))
        return

    # Text output with day grouping for week view
    if header:
        print(header)
        print("=" * len(header))
    
    if not selected:
        print("Keine Veranstaltungen.")
        return
    
    # Group by day for week view
    if args.week:
        from itertools import groupby
        grouped = groupby(selected, key=lambda e: e["start"].date())
        for d, events_on_day in grouped:
            day_dt = datetime.combine(d, datetime.min.time())
            print(f"\n{day_dt.strftime('%A, %d.%m.%Y')}:")
            for e in events_on_day:
                print("  " + event_to_line(e))
    else:
        for e in selected:
            print(event_to_line(e))

if __name__ == "__main__":
    main()
