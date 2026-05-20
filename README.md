# OpenClaw Skills

Custom skills for [OpenClaw](https://openclaw.ai) / CLIFFFORD.

## Skills

| Skill | Description |
|-------|-------------|
| [bahn](bahn/) | Deutsche Bahn connections, delays, tickets via db-vendo-client |
| [dwd-weather](dwd-weather/) | German weather forecasts & warnings via DWD (bund.dev) API |
| [excel-xlsx](excel-xlsx/) | Create, inspect, and edit Microsoft Excel workbooks and XLSX files |
| [fbi-wanted](fbi-wanted/) | Query the FBI Wanted public API for wanted persons and fugitives |
| [geo](geo/) | Geocoding, POI search, station lookup via OpenStreetMap |
| [git](git/) | Git commits, branches, rebases, merges, conflict resolution, history recovery |
| [humanizer](humanizer/) | Remove signs of AI-generated writing from text |
| [ical-calendar](ical-calendar/) | Reliable iCal calendar parsing for student schedules and exams |
| [ilias-sync](ilias-sync/) | ILIAS learning platform synchronization |
| [kimi-code](kimi-code/) | Boilerplate code generation via Kimi CLI |
| [liver](liver/) | BAC tracking CLI tool for alcohol consumption monitoring |
| [mensa-karlsruhe](mensa-karlsruhe/) | Meal plans for Studierendenwerk Karlsruhe canteens |
| [nearby-search](nearby-search/) | Search for nearby places via Google Maps using SerpAPI |
| [notion-cli](notion-cli/) | Notion operations via the official Notion CLI (ntn) |
| [pdf-maker](pdf-maker/) | Convert text, Markdown, or HTML to PDF documents |
| [skill-smith](skill-smith/) | Guide for creating effective skills for OpenClaw agents |
| [source-suche](source-suche/) | Search archived sources (Twitter, articles, threads) via QMD |
| [word-docx](word-docx/) | Create, inspect, and edit Microsoft Word documents and DOCX files |

## Setup

Clone into `~/.openclaw/skills/` and restart the gateway.

```bash
git clone git@github.com:Philipp-Pfeiffer/skills.git ~/.openclaw/skills
```

## Dependencies

**bahn:**
```bash
cd ~/.openclaw/skills/bahn && npm install
```

**dwd-weather:**
```bash
pip install -r ~/.openclaw/skills/dwd-weather/requirements.txt
```

**mensa-karlsruhe:**
```bash
pip install -r ~/.openclaw/skills/mensa-karlsruhe/requirements.txt
```

## Acknowledgements

- **bahn** — Based on [bahn skill by jjannix](https://github.com/jjannix/openclaw-skills/tree/master/bahn)
