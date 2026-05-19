---
name: kimi-code
description: "Nutze die Kimi CLI (kimi) für Boilerplate-Code-Generierung. Auslöser: explizite Anfrage für Boilerplate, Scaffold, oder Code-Skelette. Nicht für komplexe Logik oder Architektur — dafür mein eigenes Reasoning."
---

# Kimi Code — Boilerplate CLI

## Basics

Kimi CLI ist installiert unter `$HOME/.local/bin/kimi` (Alias: `kimi`).

```bash
kimi [OPTIONS]
```

## Wichtigste Flags

| Flag | Beschreibung |
|------|-------------|
| `-w, --work-dir <path>` | Arbeitsverzeichnis für das Projekt |
| `-p, --prompt <text>` | Prompt direkt übergeben (non-interactive) |
| `--print` | Non-interactive Modus, Output direkt auf stdout |
| `-y, --yolo` | Alle Aktionen automatisch bestätigen |
| `--model <model>` | Modell-Auswahl (default ist in config) |
| `-S, --session <id>` | Session fortsetzen |
| `--continue` | Letzte Session fortsetzen |

## Workflow für Boilerplate

### 1. Projekt-Verzeichnis erstellen

```bash
mkdir -p /pfad/zum/projekt
```

### 2. Kimi mit Prompt aufrufen

```bash
kimi -w /pfad/zum/projekt \
  -p "Create a simple Python CLI tool with argparse and logging." \
  --print -y
```

### 3. Ergebnis prüfen

Kimi erstellt die Dateien direkt im Work-Directory. Prüfe mit:
```bash
ls -la /pfad/zum/projekt
```

## Anwendungsfälle

- **Python CLI Tools** — argparse, logging, main()
- **React/Next.js Komponenten** — einfache UI-Bausteine
- **API Skelette** — FastAPI, Flask Endpoints
- **Config-Dateien** — package.json, pyproject.toml, etc.
- **Dockerfiles / GitHub Actions** — Standard-Templates

## Wann nicht Kimi nutzen

- Komplexe Architektur-Entscheidungen → eigenes Reasoning
- Code, der eigene existierende Projekte betrifft → erst nach Absprache
- Lange Multistep-Änderungen → lieber selbst schreiben

## Beispiel: Python CLI Boilerplate

```bash
kimi -w /tmp/my-cli \
  -p "Create a Python CLI tool named 'fetch' that downloads files from URLs. Use argparse, add --output flag." \
  --print -y
```
