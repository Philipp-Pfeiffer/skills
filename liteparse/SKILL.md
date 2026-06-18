---
name: liteparse
description: "Parse PDFs, Office-Dokumente und Bilder mit LiteParse — dem lokalen, Open-Source Dokumenten-Parser von LlamaIndex. Use when: (1) Text aus PDFs extrahieren, (2) JSON mit Bounding Boxes generieren, (3) Seiten-Screenshots erstellen, (4) Batch-Processing ganzer Ordner, (5) Dokumente fuer LLM-Pipelines vorbereiten. Unterstuetzt PDF, DOCX, XLSX, PPTX, Bilder. Kein Cloud-API-Key noetig."
---

# LiteParse Skill

LiteParse ist ein lokaler, model-free Dokumenten-Parser. CLI-Tool (`lit`) ist global installiert via `npm i -g @llamaindex/liteparse`.

## Quick Start

```bash
# Einzelne PDF parsen (Plain Text)
lit parse document.pdf

# JSON mit Bounding Boxes
lit parse document.pdf --format json -o output.json

# Seiten-Screenshots
lit screenshot document.pdf -o ./screenshots

# Batch: ganzer Ordner
lit batch-parse ./input ./output
```

## Workflows

### 1. Text-Extraktion für LLM-Kontext

```bash
lit parse document.pdf --format text -o doc.txt
cat doc.txt | head -c 100000  # ersten 100k Zeichen für Prompt
```

### 2. Strukturierte JSON mit Layout

```bash
lit parse document.pdf --format json -o doc.json
```

Output enthält pro Element:
- `text` — extrahierter Text
- `bbox` — `[x1, y1, x2, y2]` Bounding Box
- `page` — Seitennummer
- `type` — Titel, Paragraph, etc.

### 3. Screenshots für Vision-LLMs

```bash
lit screenshot document.pdf -o ./shots --dpi 200
```

DPI steuert Auflösung. 150 = Standard, 300 = hochauflösend.

### 4. Batch-Processing Pipeline

```bash
# Alle PDFs im Ordner
lit batch-parse ./pdfs ./parsed --format json

# Mit Extension-Filter
lit batch-parse ./docs ./parsed --extension .pdf --format json
```

### 5. Non-PDF Formate (DOCX, XLSX, PPTX, Bilder)

LibreOffice und ImageMagick müssen installiert sein:
```bash
# Arch Linux
sudo pacman -S libreoffice-fresh imagemagick
```

LiteParse konvertiert automatisch zu PDF vor dem Parsing.

## Wichtige CLI-Optionen

| Flag | Bedeutung |
|------|-----------|
| `--format json\|text` | Output-Format |
| `--no-ocr` | OCR deaktivieren (schneller) |
| `--ocr-language fra` | OCR-Sprache (Tesseract-Format) |
| `--target-pages "1-5,10"` | Nur bestimmte Seiten |
| `--dpi 200` | Rendering-Auflösung |
| `--max-pages 50` | Limitieren |
| `--num-workers 4` | Parallel-OCR-Worker |
| `-q` | Quiet-Modus |

## LiteParse vs. LlamaParse

| | LiteParse | LlamaParse |
|---|---|---|
| Kosten | Kostenlos, lokal | Cloud, proprietär |
| Komplexe Tabellen | Begrenzt | Exzellent |
| Layout-Detection | Basic | Advanced |
| Bild-Extraktion | Screenshots | Native |
| Markdown-Output | – | Ja |
| Szenario | Einfache Dokumente, Batch | Produktions-Pipelines |

## Agent-Integration

LiteParse hat eine offizielle Agent-Skill:
```bash
npx skills add run-llama/llamaparse-agent-skills --skill liteparse
```

Oder manuell: `~/.openclaw/skills/liteparse/references/integration-guide.md`

## Vollständige Referenz

- CLI-Referenz: `references/cli-reference.md`
- Integration-Guide: `references/integration-guide.md`
