# Nearby Search Skill

Ein generischer Skill für Agent-Frameworks, um Orte in der Nähe zu finden — Cafés, Restaurants, Bäckereien, oder beliebige POIs.

## Funktionsweise

Der Skill nutzt **SerpAPI Google Maps Search**, um Orte zu finden, und berechnet die exakte Distanz vom aktuellen Standort mittels Haversine-Formel.

## Nutzung

```bash
python search.py <lat> <lon> "[Suchbegriff]" [Radius_in_m]
```

Beispiele:
```bash
python search.py 49.009 8.418 "Café" 1000
python search.py 49.009 8.418 "Restaurant" 2000
python search.py 49.009 8.418 "Frühstück" 500
```

## Config

Vor der ersten Nutzung müssen zwei Dateien im `config/`-Ordner angelegt werden:

### 1. API-Key: `config/serpapi.env`
```bash
SERPAPI_KEY="dein-key-hier"
```
→ Hole dir einen kostenlosen Key bei [serpapi.com](https://serpapi.com)

### 2. Orts-Aliasse: `config/locations.json`
```json
{
  "kit": {"lat": 49.009, "lon": 8.418, "label": "KIT Campus Süd"},
  "home": {"lat": 0.0, "lon": 0.0, "label": "Zuhause"},
  "arbeit": {"lat": 0.0, "lon": 0.0, "label": "Büro"}
}
```

**Wichtig:** `config/` ist via `.gitignore` ausgeschlossen. Die Dateien bleiben lokal.

## Ausgabe

Die Ausgabe erfolgt als **Liste** (nicht Tabelle), da Tabellen in Messaging-Apps wie WhatsApp nicht gut rendern:

```
📍 Café Palaver — ⭐ 4.4 (1.411 Reviews) — 836m — Cafe
📍 Little Base — ⭐ 4.5 (219 Reviews) — 266m — Cafe
📍 Restaurant Ege Rosa — ⭐ 4.7 (589 Reviews) — 2.191m — Breakfast restaurant
```

## Agent-Integration

Wenn ein Agent diesen Skill nutzt:

1. **Immer nachfragen**, wenn der Standort unklar ist ("Wo bist du gerade?")
2. **Immer nachfragen**, wenn der Radius nicht angegeben wurde ("Wie weit darf es sein? 500m? 1km?")
3. Nutze gespeicherte Orts-Aliasse aus `locations.json` für bekannte Locations
4. Die Ausgabe soll als nummerierte Liste formatiert werden

## Dependencies

- Python 3.8+
- `requests` (`pip install requests`)

## Kosten

- SerpAPI Free-Tier: 100 Searches/Monat
- Pro Request: 1 Google Maps Search
- Keine zusätzlichen Requests für Details nötig (Koordinaten inklusive)
