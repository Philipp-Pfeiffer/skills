# Mensa Karlsruhe Skill für KI-Agenten

## Überblick

Dieser Skill ermöglicht den Zugriff auf die täglichen Speisepläne der Mensen des Studierendenwerks Karlsruhe. Der KI-Agent kann damit Benutzern helfen, das aktuelle Essensangebot zu finden, nach bestimmten Gerichten zu suchen und Informationen über Preise und Nährwerte zu erhalten.

## Verfügbare Commands

### 1. list_canteens
Gibt eine Liste aller verfügbaren Mensen zurück.

**Verwendung:**
```
python mensa_simple.py canteens
```
Oder im MCP Tool: `get_canteens`

**Beispiel-Prompt:** "Welche Mensen gibt es in Karlsruhe?"

---

### 2. todays_meals
Liefert den heutigen Speiseplan, optional gefiltert nach Mensen.

**Parameter:**
- `canteens` (optional): Liste von Mensen-IDs z.B. `["adenauerring", "moltke"]`

**Verwendung:**
```
python mensa_simple.py today adenauerring
python mensa_simple.py today adenauerring,moltke
```
Oder im MCP Tool: `get_todays_meals` mit `{"canteens": ["adenauerring"]}`

**Beispiel-Prompt:** "Was gibt es heute in der Mensa am Adenauerring?"

---

### 3. meals_by_date
Speiseplan für ein bestimmtes Datum abrufen.

**Parameter:**
- `date` (erforderlich): Datum im Format `YYYY-MM-DD`
- `canteens` (optional): Liste von Mensen-IDs

**Verwendung:**
```
python mensa_simple.py date 2026-05-01 adenauerring
```
Oder im MCP Tool: `get_meals_by_date` mit `{"date": "2026-05-01", "canteens": ["adenauerring"]}`

**Beispiel-Prompt:** "Was gibt es morgen in der Mensa?"

---

### 4. search_meals
Suche nach Gerichten basierend auf einem Stichwort.

**Parameter:**
- `query` (erforderlich): Suchbegriff (z.B. "vegetarisch", "vegan", "Pizza", "Curry")
- `days` (optional): Anzahl der Tage zum Durchsuchen (Standard: 3, Max: 7)

**Verwendung:**
```
python mensa_simple.py search vegan 5
python mensa_simple.py search Curry 3
```
Oder im MCP Tool: `search_meals` mit `{"query": "vegan", "days": 5}`

**Beispiel-Prompts:**
- "Gibt es heute etwas Vegetarisches?"
- "Finde alle veganen Gerichte für diese Woche"
- "Zeig mir alle Curry-Gerichte"

---

### 5. legend
Erklärung der Zusatzstoffe und Nährwert-Klassifizierungen.

**Verwendung:**
```
python mensa_simple.py legend
```
Oder im MCP Tool: `get_legend`

**Beispiel-Prompt:** "Was bedeutet VG bei den Gerichten?"

---

## Mensen-Übersicht

| ID | Name | Standort |
|---|---|---|
| `adenauerring` | Mensa Am Adenauerring | KIT Campus |
| `moltke` | Mensa Moltke | Nähe KIT |
| `x1moltkestrasse` | Menseria Moltkestraße 30 | Moltkestraße |
| `erzberger` | Mensa Erzbergerstraße | Erzbergerstraße |
| `gottesaue` | Menseria Schloss Gottesaue | Schloss Gottesaue |
| `tiefenbronner` | Mensa Tiefenbronnerstraße | Tiefenbronnerstraße |
| `holzgarten` | Mensa Holzgartenstraße | Holzgartenstraße |

---

## Klassifizierungs-Codes

Diese Codes erscheinen bei jedem Gericht:

| Code | Bedeutung |
|---|---|
| `VG` | Vegetarisch |
| `V` / `VEG` | Vegan |
| `G` | Geflügel |
| `R` | Rind |
| `S` | Schwein |
| `F` | Fisch |
| `L` | Lamm |

---

## Prompt-Vorlagen für Agenten

### Tageszusammenfassung
```
Gib mir eine Zusammenfassung des heutigen Essensangebots in der Mensa Am Adenauerring. 
Liste die Hauptgerichte mit Preisen auf.
```

### Vegetarische Optionen
```
Finde alle vegetarischen Gerichte für heute und morgen.
```

### Günstigste Option
```
Was ist das günstigste vegane Gericht heute?
```

### Nach Zutat suchen
```
Gibt es heute etwas mit [Zutat]? (z.B. "Spinat", "Tofu", "Lachs")
```

### Mensen vergleichen
```
Vergleiche das Angebot der Mensa Moltke mit der Mensa am Adenauerring heute.
```

---

## Integration mit KI-Agenten

### Claude Desktop
In `~/.config/claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "mensa-karlsruhe": {
      "command": "python",
      "args": ["/path/to/skills/mensa-karlsruhe/mensa_stdio_server.py"]
    }
  }
}
```

### Ollama mit opencode
In `~/.opencode/mcp.json`:
```json
{
  "mcpServers": {
    "mensa": {
      "command": "python",
      "args": ["/absolute/path/to/skills/mensa-karlsruhe/mensa_stdio_server.py"]
    }
  }
}
```

### Direkte Python-Nutzung
```python
import asyncio
from mensa_adapter import get_todays_meals, search_meals, format_meal_for_llm

async def main():
    # Heutige Gerichte
    plan = await get_todays_meals(canteens=["adenauerring"])
    print(format_meal_for_llm(plan))
    
    # Nach Gerichten suchen
    results = await search_meals("vegan", days=3)

asyncio.run(main())
```

---

## Fehlerbehandlung

- **404 Not Found**: Kein Speiseplan für dieses Datum verfügbar
- **Connection Error**: API nicht erreichbar, später erneut versuchen
- **Timeout**: Anfrage dauert zu lange, ggf. mit weniger Tagen wiederholen

---

## Datenquelle

- API: `https://mensa-api.fnka.de`
- Basierend auf: [ka-mensa-api](https://github.com/meyfa/ka-mensa-api) (MIT License)
- Echtzeit-Daten vom Studierendenwerk Karlsruhe
