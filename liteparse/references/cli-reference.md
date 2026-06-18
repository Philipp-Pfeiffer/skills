# LiteParse CLI-Referenz

## Installation

```bash
npm i -g @llamaindex/liteparse
# oder: pip install liteparse
# oder: cargo install liteparse
```

CLI-Name: `lit`

---

## Befehle

### `lit parse <file>`

Einzelnes Dokument parsen.

**Optionen:**
- `-o, --output <file>` — Output-Dateipfad
- `--format <format>` — `json` oder `text` (Default: text)
- `--no-ocr` — OCR deaktivieren
- `--ocr-language <lang>` — Tesseract-Sprachcode (Default: `eng`)
- `--ocr-server-url <url>` — Eigenen OCR-Server verwenden
- `--tessdata-path <path>` — Tesseract-Datenverzeichnis
- `--max-pages <n>` — Max. Seiten (Default: 1000)
- `--target-pages <pages>` — Seiten-Selektion, z.B. `"1-5,10,15-20"`
- `--dpi <dpi>` — Rendering-DPI (Default: 150)
- `--preserve-small-text` — Sehr kleinen Text behalten
- `--password <password>` — Für verschlüsselte Dokumente
- `--num-workers <n>` — Parallele OCR-Worker (Default: CPU Kerne - 1)
- `-q, --quiet` — Progress unterdrücken
- `-h, --help`

**Beispiele:**
```bash
lit parse report.pdf
lit parse report.pdf --format json -o report.json
lit parse report.pdf --target-pages "1-10" --no-ocr
lit parse scan.pdf --ocr-language deu --dpi 300
```

---

### `lit batch-parse <input-dir> <output-dir>`

Ganze Ordner parsen.

**Zusätzliche Optionen:**
- `--recursive` — Rekursiv Unterordner durchsuchen
- `--extension <ext>` — Nur bestimmte Extension, z.B. `.pdf`

**Beispiele:**
```bash
lit batch-parse ./pdfs ./parsed --format json
lit batch-parse ./docs ./parsed --extension .pdf --recursive
```

---

### `lit screenshot <file>`

Seiten als PNG-Screenshots rendern.

**Optionen:**
- `-o, --output-dir <dir>` — Default: `./screenshots`
- `--target-pages <pages>` — Selektion
- `--dpi <dpi>` — Default: 150
- `--password <password>`
- `-q, --quiet`
- `-h, --help`

**Beispiele:**
```bash
lit screenshot document.pdf -o ./shots
lit screenshot document.pdf --target-pages "1,3,5" --dpi 300
```

---

## Umgebungsvariablen

| Variable | Beschreibung |
|----------|-------------|
| `TESSDATA_PREFIX` | Pfad zu Tesseract `.traineddata` Dateien. Für Offline/Air-gapped Umgebungen. |

---

## Input-Formate

### Native (ohne Konverter)
- PDF

### Mit LibreOffice (Konvertierung zu PDF)
- Word: `.doc`, `.docx`, `.docm`, `.odt`, `.rtf`, `.pages`
- PowerPoint: `.ppt`, `.pptx`, `.pptm`, `.odp`, `.key`
- Spreadsheets: `.xls`, `.xlsx`, `.xlsm`, `.ods`, `.csv`, `.tsv`, `.numbers`

### Mit ImageMagick (Konvertierung zu PDF)
- Bilder: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.tiff`, `.webp`, `.svg`

---

## OCR-Systeme

### Built-in (Default)
- **Tesseract** — Gebündelt, zero setup

### HTTP OCR Server (optional)
Eigenen OCR-Server integrieren via `--ocr-server-url`.

API-Spezifikation:
- `POST /ocr`
- Body: `file` + `language`
- Response: `{ results: [{ text, bbox: [x1,y1,x2,y2], confidence }] }`

Beispiel-Implementierungen:
- EasyOCR
- PaddleOCR

---

## Output-Formate

### Text
Plain text, Layout-erhalten (Zeilenumbrüche, Absätze).

### JSON
```json
{
  "pages": [
    {
      "page": 1,
      "elements": [
        {
          "text": "Kapitel 1",
          "bbox": [100, 50, 300, 80],
          "type": "title"
        }
      ]
    }
  ]
}
```

### Screenshots
PNG-Dateien, benannt nach Seitennummer.

---

## Architektur

```
PDF → PDFium (Text-Extraction) → OCR (Tesseract/HTTP) → Merge → Grid Projection → Output
DOCX/XLSX/PPTX/Images → LibreOffice/ImageMagick → PDF → ...
```

Komponenten:
- **PDFium** — Google Chrome's PDF-Engine (C-Library)
- **Tesseract** — OCR-Engine
- **Rust Core** — Performance-kritische Pipeline
- **Bindings** — Node.js (napi-rs), Python (PyO3), WASM (wasm-bindgen)
