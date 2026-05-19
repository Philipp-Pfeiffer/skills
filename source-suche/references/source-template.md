# Quellen-Template

## Twitter / X-Thread

```markdown
---
source: https://x.com/handle/status/1234567890
author: @handle
date: 2026-04-26
tags: [ki, ml, policy]
status: unread
---

## Kernpunkte

- Punkt 1
- Punkt 2
- Punkt 3

## Warum relevant

Kurze Begründung, warum dies archiviert wurde.

## Original-Text (wichtigste Tweets)

> Tweet 1: ...

> Tweet 2: ...
```

## Artikel / Blogpost

```markdown
---
source: https://example.com/article
author: Autor Name
date: 2026-04-26
tags: [tooling, rust]
status: unread
---

## Zusammenfassung

3-5 Sätze zum Inhalt.

## Key Quotes

> "Wichtiges Zitat aus dem Artikel."

## Warum archiviert

Eigenes Interesse / Future Reference.
```

## Status-Bedeutung

| Status | Bedeutung |
|--------|-----------|
| `unread` | Roh-abgelegt, noch nicht durchgelesen |
| `skimmed` | Überflogen, grobe Idee bekannt |
| `distilled` | Wichtige Erkenntnisse extrahiert, ggf. ins Memory-Netz überführt |

## Regeln

1. **Immer Frontmatter** — sonst findet QMD die Datei nicht sinnvoll
2. **Tags sind frei** — aber konsistent halten (z.B. immer `ki` statt `ai`, `ml`)
3. **Status pflegen** — beim Durchlesen auf `skimmed` oder `distilled` aktualisieren
4. **Keine Screenshot-Archive** — Text ist durchsuchbar, Bilder nicht
5. **Dateiname** — `YYYY-MM-DD_author_thema.md` oder `YYYY-MM-DD_handle_tweet-thread.md`
