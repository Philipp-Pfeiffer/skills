# LiteParse Integration-Guide

## Für LLM/Agent-Pipelines

### 1. Text → LLM Prompt

```bash
# Extrahieren und direkt pipen
lit parse doc.pdf -q | llm-model-prompt

# Oder Zwischenspeichern
lit parse doc.pdf -o doc.txt
cat doc.txt | head -c 100000 > prompt-context.txt
```

Chunking-Strategie für lange Dokumente:
- JSON-Output nutzen → pro Seite/Element chunken
- Bounding boxes für semantische Chunking-Grenzen nutzen

### 2. JSON → Vector Store

```bash
lit parse doc.pdf --format json -o doc.json
```

Python-Pipeline:
```python
import json
from liteparse import parse

result = parse("doc.pdf", format="json")
for page in result["pages"]:
    for element in page["elements"]:
        text = element["text"]
        bbox = element["bbox"]
        # Embedding + Metadata speichern
        store.add(text, metadata={"page": page["page"], "bbox": bbox})
```

### 3. Screenshots → Vision-LLM

```bash
lit screenshot doc.pdf -o ./shots --dpi 200
```

Für GPT-4V/Claude Vision:
- Screenshots + extrahierter Text als Kontext
- Bounding boxes verlinken Text mit visueller Position

### 4. RAG-Pipeline

```
Dokument → LiteParse (JSON) → Chunking → Embeddings → Vector DB
                                    ↓
                              Screenshots → Vision-LLM (optional)
```

### 5. LiteParse vs. LlamaParse in Produktion

| Szenario | Empfohlener Parser |
|----------|-------------------|
| Schneller Prototyp, lokale Entwicklung | LiteParse |
| Batch-Processing 1000+ Dokumente | LiteParse (parallel) |
| Komplexe Tabellen, Charts, Scans | LlamaParse (Cloud) |
| Air-gapped, sensible Daten | LiteParse |
| Markdown-Output für RAG | LlamaParse |

## Agent-Skill

Offizielle Integration:
```bash
npx skills add run-llama/llamaparse-agent-skills --skill liteparse
```

Oder manuell die SKILL.md kopieren:
https://github.com/run-llama/llamaparse-agent-skills/tree/main/skills/liteparse

## Fehlerbehandlung

| Problem | Lösung |
|---------|--------|
| "LibreOffice not found" | `sudo pacman -S libreoffice-fresh` |
| "ImageMagick not found" | `sudo pacman -S imagemagick` |
| OCR langsam | `--no-ocr` für native PDFs, `--num-workers 8` |
| Tesseract Sprache fehlt | `TESSDATA_PREFIX` setzen oder `--tessdata-path` |
| Encrypted PDF | `--password` nutzen |

## Performance-Tuning

```bash
# Maximale Geschwindigkeit (kein OCR)
lit parse doc.pdf --no-ocr

# Hohe Qualität Scans
lit parse scan.pdf --dpi 300 --ocr-language deu --num-workers 8

# Batch mit vielen Cores
lit batch-parse ./in ./out --format json --num-workers 16
```
