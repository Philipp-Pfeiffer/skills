# OpenClaw Skills

Custom skills for [OpenClaw](https://openclaw.ai) / CLIFFFORD.

## Skills

| Skill | Description |
|-------|-------------|
| [bahn](bahn/) | Deutsche Bahn connections, delays, tickets via db-vendo-client |
| [browser-to-api](browser-to-api/) | Replay-driven API discovery from browser traces |
| [dwd-weather](dwd-weather/) | German weather forecasts & warnings via DWD (bund.dev) API |
| [geo](geo/) | Geocoding, POI search, station lookup via OpenStreetMap |
| [kimi-code](kimi-code/) | Boilerplate code generation via Kimi CLI |
| [mensa-karlsruhe](mensa-karlsruhe/) | Meal plans for Studierendenwerk Karlsruhe canteens |
| [notion-cli](notion-cli/) | Notion operations via notion-cli |

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
pip install pytest  # for running tests
```

**mensa-karlsruhe:**
```bash
pip install httpx
```

## Acknowledgements

- **bahn** — Based on [bahn skill by jjannix](https://github.com/jjannix/openclaw-skills/tree/master/bahn)
