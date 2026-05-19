---
name: ical-calendar
description: Reliable iCal calendar parsing for student schedules, exams, and daily planning. Use when the user asks about their university timetable, lectures today/tomorrow/this week, exam dates, or any calendar query that requires precise date/time extraction from an .ics feed. Also use in cron jobs that need deterministic schedule output. Works with KIT Campus calendar and any standard iCal URL.
---

# iCal Calendar Skill

## Purpose

Parse iCal (.ics) feeds reliably using only Python standard library — no external dependencies. This makes it safe for cron jobs and long-term use without pip rot.

Default URL: Philipp's KIT Campus calendar (`https://campus.kit.edu/sp/webcal/AOpeOURNuA`). Override via `--url` or `ICAL_URL` env.

## Core Script

**`scripts/parse_ical.py`**

Run it directly:

```bash
python3 scripts/parse_ical.py --today
python3 scripts/parse_ical.py --tomorrow
python3 scripts/parse_ical.py --week
python3 scripts/parse_ical.py --exams
python3 scripts/parse_ical.py --next-exam
python3 scripts/parse_ical.py --date 2026-07-15
python3 scripts/parse_ical.py --raw   # dump everything as JSON
```

Environment variables:
- `ICAL_URL` — override the default calendar URL

### Flags

| Flag | Output |
|------|--------|
| `--today` | Events for today (default if no flag) |
| `--tomorrow` | Events for tomorrow |
| `--week` | Monday–Sunday of current week |
| `--date YYYY-MM-DD` | Events for specific date |
| `--exams` | All events matching exam heuristics |
| `--next-exam` | Single next upcoming exam |
| `--raw` | Full JSON dump of all parsed events |
| `--json` | JSON output for the selected filter |
| `--file path.ics` | Read from local file instead of URL |

## Integration Patterns

### Cron / Morning Report

```bash
# In a cron job or heartbeat script
python3 ~/.openclaw/workspace/skills/ical-calendar/scripts/parse_ical.py --today
```

Always use `--today`, `--tomorrow`, or `--week` for scheduled reports. Avoid `--raw` in cron — too verbose.

### Answering User Questions

- **"Was habe ich heute?"** → `--today`
- **"Wann sind meine Klausuren?"** → `--exams` or `--next-exam`
- **"Wann ist die nächste Prüfung?"** → `--next-exam`
- **"Was steht am 15.07.?"** → `--date 2026-07-15`

### Output Format

Plain text, one line per event:

```
08:00-09:30: Betriebssysteme @ HS37
11:30-13:00: Theoretische Grundlagen der Informatik @ Gerthsen
```

German day names are used for headers. No markdown tables — WhatsApp-safe.

## Exam Detection

Heuristic keywords in summary + description:
`klausur`, `prüfung`, `exam`, `test`, `mündlich`, `zwischenklausur`

If `--exams` returns nothing, the feed simply contains no matching events.

## Error Handling

- HTTP errors print to stderr and exit 1
- Empty feeds print "Keine Veranstaltungen."
- Malformed lines are skipped silently during parse

## No External Dependencies

The parser handles:
- RFC 5545 line unfolding
- Date-time and date-only values
- Timezone labels (naive, no offset math — assumes local time)

What it does **not** handle (and does not need for student schedules):
- RRULE recurrence expansion
- VTIMEZONE offset calculations
- Alarms / VALARM
