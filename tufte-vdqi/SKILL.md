---
name: tufte-vdqi
description: Produce Tufte-style data visualizations — minimal ink, honest proportions, range-frame axes, direct labels. Assess existing charts for graphical excellence, render clean SVGs, and wrap them in Tufte-styled HTML. Use whenever Philipp wants a chart, a data visualization critique, or a clean time-series/bars/scatter plot.
---

# Tufte VDQI — Visual Display of Quantitative Information

## Meine Tools

- `scripts/render_line_svg.py` — SVG-Liniencharts mit range-frame axes, direkten Labels, kein Grid
- `scripts/deflate.py` — Inflationsanpassung für Währungszeitreihen (braucht echte CPI-Daten)
- `scripts/wrap_html.py` — SVG in Tufte-HTML-Seite mit ET Book Typography verpacken
- `references/tufte-principles.md` — Die 9 Kriterien für grafische Exzellenz + 7 Remedies (B1–B7)

## Wann ich das nutze

- Philipp sagt: "Mach mir einen Chart", "Visualisiere das", "Plot", "Grafik"
- Philipp fragt: "Ist dieser Chart gut?", "Was ist falsch damit?", "Zu unübersichtlich"
- Währungsdaten über mehrere Jahre: automatisch deflate.py für Real-Terms
- Daten aus Logs/Tracking/Fitness/Finanzen in saubere Grafik verwandeln

## Mein Workflow

### 1. Daten sammeln
- Aus Logs, JSON, CSV, oder Philipp gibt sie direkt
- Format: `[{"x": 2000, "y": 12.1}, {"x": 2010, "y": 18.4}, ...]`

### 2. Assess (wenn Philipp einen existierenden Chart kritisiert)
- 9 Kriterien scoren (0–10, gewichtet)
- Lie factor berechnen: `visual_change_% / data_change_%` (0.95–1.05 = OK)
- Remedies B1–B7 zuordnen

### 3. Render (neuen Chart bauen)
- Build Checklist:
  - **B1 Honest proportions:** Balken starten bei Null, keine 2D/3D-Verzerrung
  - **B2 Range frames:** Achsenlinie spannt exakt Daten min..max, Enden beschriftet
  - **B3 Small multiples:** Bei vielen Serien — wiederholtes Design, shared scales
  - **B4 Direct labels:** Labels auf den Daten, keine separate Legend
  - **B5 Minimal ink:** Weißer Hintergrund, keine Gridlines, keine Borders, kein 3D
  - **B6 One encoding per datum:** Keine Duplikate (Höhe + Farbe + Label)
  - **B7 Money over time:** Nominal → Real-Terms mit deflate.py

### 4. Output
- SVG: portabel, einzelne Datei
- HTML: Tufte-styled Seite mit Caption (via wrap_html.py)
- Pfad zurückgeben, wo die Datei liegt

## Befehle

```bash
# Line Chart SVG
python ~/.openclaw/skills/tufte-vdqi/scripts/render_line_svg.py \
  --data '[{"x":2000,"y":12.1},{"x":2010,"y":18.4},{"x":2023,"y":22.9}]' \
  --title "Revenue (real 2023 USD, M)" --series "Revenue" \
  --out /tmp/chart.svg

# Inflationsanpassung
python ~/.openclaw/skills/tufte-vdqi/scripts/deflate.py \
  --values 40000,50000,60000 --years 2005,2015,2023 \
  --cpi '{"2005":195.3,"2015":237.0,"2023":304.7}' \
  --base-year 2023 --label "real 2023 USD"

# HTML Wrapper
python ~/.openclaw/skills/tufte-vdqi/scripts/wrap_html.py \
  --svg /tmp/chart.svg --out /tmp/chart.html \
  --title "Revenue, 2000–2023" \
  --caption "Inflation-adjusted to 2023 USD using BLS CPI-U."
```

## Limitierungen

- Line charts: render_line_svg.py ist sofort einsatzbereit
- Bar, scatter, small multiples: muss ich manuell als SVG/HTML schreiben (nach Build Checklist)
- CPI-Daten: muss ich bei Bedarf per Web-Suche besorgen (BLS, Eurostat), deflate.py hat keine eingebaute Tabelle
- Kein Matplotlib/Seaborn — reines SVG für maximale Kontrolle über jedes Ink-Pixel

## Beispiel-Anfragen

- "Plot meine Push-up-Progression aus dem Lift-Log"
- "Ist dieser Chart aus der Präsentation gut?"
- "Visualisiere den Kaffeepreis über die letzten 10 Jahre"
- "Mach einen Tufte-Chart aus meinen Trainingsdaten"

## Verwandte Skills

- `assess-graphical-excellence` — intern, über tufte-principles.md
- `render-tufte-chart` — intern, über die Python-Scripts
