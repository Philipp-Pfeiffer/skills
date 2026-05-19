---
name: liver
description: BAC (Blood Alcohol Content) tracking CLI tool for personal alcohol consumption monitoring. Use when the user needs to track drinks, calculate BAC curves, estimate sober time, manage drinking presets/sessions, or configure their liver profile. Triggers on mentions of liver, BAC, alcohol tracking, drink logging, or sober estimation. NOT for the mnafees/liver live-reloading file watcher.
---

# liver — BAC Tracking CLI

Personal alcohol consumption tracker with pharmacokinetic BAC calculations.

**Package:** `liver-cli` (npm)  
**Binary:** `liver`  
**Repo:** https://github.com/Philipp-Pfeiffer/liver-cli  
**Version:** v0.1.2 (main branch enthält v0.2.0-Features: ethanol-rs WASM, Active Drink, SVG Export)

## GitHub Repository
```
https://github.com/Philipp-Pfeiffer/liver-cli
```
Main branch aktualisieren:
```bash
cd /tmp/liver-cli && git checkout main && git pull && npm install && npm run build && npm link
```
Hinweis: Nach `npm run build` muss `vendor/` in `dist/` kopiert werden und der WASM-Pfad in `dist/index.js` gepatcht werden (`../../vendor` → `./vendor`).

## Installation

```bash
npm install -g liver-cli
```

Requires Node.js ≥ 22.

## Global Flags

| Flag | Description |
|------|-------------|
| `-V, --version` | Version output |
| `--human` | Human-readable output |
| `--no-color` | Disable colors (or `NO_COLOR=1`) |
| `-v, --verbose` | Verbose logging |
| `--formula <watson\|widmark>` | Override BAC formula |

## Commands

### Profile Setup (once)

```bash
liver profile set --weight <kg> --height <cm> --sex <m/f/o> --age <jahre> [--formula watson]
liver profile show
```

| Field | Description |
|-------|-------------|
| `--weight` | Body weight in kg |
| `--height` | Height in cm |
| `--sex` | `m` / `f` / `o` |
| `--age` | Age in years |
| `--formula` | `watson` (default) or `widmark` |

### Drink Presets

```bash
liver preset set <name> --vol 500 --abv 5.2    # Create/update preset
liver preset list                               # List all presets
liver preset show <name>                        # Show preset details
liver preset rm <name>                          # Remove preset
```

### Sessions

```bash
liver session start --name "Friday Night" --stomach full [--at <T>]
liver session show                              # Current session info
liver session end [--at <T>]                    # End session
liver session list [--month 2026-04]            # List past sessions
liver session stomach <empty|some|full>         # Change stomach state mid-session
liver session rename <id> --name <str>          # Rename session
```

### Adding Drinks

```bash
# Via preset
liver add augustiner [--at <T>] [--duration 30m]

# Inline (no preset)
liver add --vol 500 --abv 5.2 [--at <T>] [--duration 30m]

# Start a drink (tracks open drink until stop)
liver start <preset> [--at <T>] [--duration 30m] [--force]
liver stop [--at <T>]
```

| Option | Description |
|--------|-------------|
| `--vol` | Volume in milliliters |
| `--abv` | Alcohol by volume in percent |
| `--at <T>` | Timestamp (ISO or natural language via chrono-node) |
| `--duration <Xm\|Xh>` | Drinking duration (e.g., `30m`, `2h`) |
| `--stomach <empty\|some\|full>` | Stomach state for absorption rate |
| `--session new` | Create new session for backdated drink |
| `--force` | Stop current drink and start new one |

### Status & Computation

```bash
liver status                    # Current BAC and session info
liver bac --at <T>              # BAC at specific time
liver curve --from <T> --to <T> --step 5m   # BAC curve over time range
liver sober                     # Minutes until sober (BAC ≤ 0.01‰)
```

### Statistics

```bash
liver stats --month 2026-04     # Monthly stats
liver stats --year 2026         # Yearly stats
liver stats --from <T> --to <T> # Date range
liver stats --all               # All-time stats
```

### Drink Management

```bash
liver drink list                # List all drinks
liver drink rm <id>              # Remove a drink by ID
```

### Configuration

```bash
liver config set <key> <value>   # Set config value
liver config get <key>           # Get config value
liver config list                 # List all config
```

## Key Behaviors

- **One open drink at a time** — `start` without `--force` blocks if a drink is already open
- **Lazy session auto-close** — Sessions close automatically on the next command if > wall-clock threshold
- **Stomach states affect absorption:** `empty` (fastest), `some`, `full` (slowest)
- **BAC formulas:** Watson (default) or Widmark via `--formula`
- **Time parsing:** chrono-node supports natural language (`"2 hours ago"`, `"2026-04-30 18:00"`)
- **Output format:** JSON by default; `--human` for readable text

## Resources

- **Full spec coverage & ADRs**: `references/spec-coverage.md`
- **Engine model docs**: `references/ADR-002.md`
- **Verification reports**: `references/FIX_PASS_*.md`
