---
name: source-suche
description: "Suche in archivierten Quellen (Twitter, Artikel, Threads) via QMD. Use when: (1) der Nutzer nach archivierten Twitter-Threads, Artikeln oder externen Quellen fragt, (2) eine Suche außerhalb des MEMORY.md / memory/ Netzwerks nötig ist, (3) der Nutzer 'meine Quellen', 'Twitter-Archiv', 'gespeicherte Artikel' o.ä. erwähnt, (4) Roh-Quellen aus workspace/sources/ durchsucht werden sollen. Nicht für MEMORY.md oder memory/ — dafür gibt es memory_search."
---

# Source-Suche

## Zweck

Dieser Skill durchsucht das lokale Quellenarchiv in `workspace/sources/` — Twitter-Threads, Artikel, gespeicherte Posts, etc. — mittels QMD (Quick Markdown Search).

**Wichtig:** `memory_search` greift NICHT auf `sources/` zu. Für Quellen-Zugriff wird QMD direkt genutzt.

## Archiv-Struktur

```
workspace/sources/
├── twitter/      — Gespeicherte Twitter/X-Threads
├── articles/     — Archivierte Artikel, Blogposts
└── threads/      — Andere Thread-Formate (Reddit, etc.)
```

Jede Datei sollte Frontmatter enthalten:

```yaml
---
source: https://x.com/...
author: @handle
date: 2026-04-26
tags: [ki, policy, tooling]
status: unread | skimmed | distilled
---
```

## Such-Workflow

### 1. Health-Check (immer zuerst)

Vor jeder Quellen-Suche: **Verifiziere, dass QMD funktioniert.**

```bash
qmd collection show sources
```

Erwartetes Ergebnis:
- Collection `sources` existiert
- `Path: $HOME/.openclaw/workspace/sources`
- `Files: N` (N > 0 wenn Quellen vorhanden)

Falls `sources` fehlt oder 0 Files trotz vorhandener Dateien:
```bash
qmd collection add sources ~/.openclaw/workspace/sources --pattern "**/*.md"
```

### 2. Suche durchführen

**Option A — Quick Search (BM25 only, schnell):**
```bash
qmd search "Suchbegriff" --collection sources
```

**Option B — Hybrid Search (empfohlen, Vektor + Text):**
```bash
qmd query "Suchbegriff" --collection sources
```

**Option C — Nur Vektor (semantisch):**
```bash
qmd vsearch "Konzept-Beschreibung" --collection sources
```

### 3. Ergebnis prüfen — Sanity Check

QMD hat in der Vergangenheit manchmal **triviale oder leere Ergebnisse** zurückgegeben. Nach der Suche:

- Sind die Ergebnisse **relevant** zum Suchbegriff?
- Enthalten sie **tatsächlichen Inhalt** (nicht nur Dateinamen)?
- Ist die **Score** sinnvoll (> 0.3)?

**Falls die Ergebnisse trivial sind (nur Dateinamen, keine Snippets, offensichtlich irrelevant):**

→ **Force-Reindex durchführen:**
```bash
qmd update --collection sources --force
qmd embed --collection sources
```

→ Dann Suche wiederholen.

→ Falls weiterhin trivial: Nutzer informieren, dass das Archiv möglicherweise leer oder nicht indexierbar ist.

### 4. Ergebnis liefern

- Datei-Pfad mit `qmd get <pfad>` laden für Volltext
- Snippets zitieren mit Source-Angabe
- Bei mehreren Treffern: priorisieren nach Relevanz + Datum

## Troubleshooting

| Problem | Lösung |
|---------|--------|
| `Collection 'sources' not found` | `qmd collection add sources ~/.openclaw/workspace/sources --pattern "**/*.md"` |
| `0 files` trotz Inhalt | `qmd update --collection sources --force` |
| Ergebnisse sind nur Dateinamen | `qmd embed --collection sources` + Suche wiederholen |
| QMD binary nicht gefunden | `export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"` |

## Wichtige Grenzen

- `memory_search` = MEMORY.md + memory/ → **nicht für Quellen**
- `qmd` = Alles im Workspace → **sources Collection explizit angeben**
- Leere oder nicht-indexierte Dateien werden nicht gefunden

## Health-Check Script

Für automatisierte Verifikation: `scripts/qmd-health-check.sh`
