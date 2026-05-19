---
name: nearby-search
description: Search for nearby places (cafés, restaurants, shops, POIs) via Google Maps using SerpAPI. Use when the user asks for places near a location, wants to find cafés or restaurants nearby, searches for points of interest with a location context, or sends a WhatsApp location to search around. Supports location aliases (kit, home, work) from config/locations.json. Output is always plain lists — never markdown tables for WhatsApp.
---

# nearby-search — SKILL.md

## Trigger
- "Cafés in der Nähe"
- "Restaurants um [Ort]"
- "Was gibt es zu essen in der Nähe"
- "Suche [Begriff] in der Nähe"
- WhatsApp-Standort senden → automatisch als Referenzpunkt nutzen

## Flow
1. Standort ermitteln (Koordinaten oder Alias aus `locations.json`)
2. Radius abfragen wenn nicht angegeben (Standard: 1500m)
3. Suchbegriff abfragen wenn nicht angegeben (Standard: "Café")
4. `search.py` ausführen
5. Ergebnis als Liste zurückgeben

## Regeln
- NIE Tabellen über WhatsApp ausgeben — immer Listen
- Immer nachfragen bei unklarem Standort oder Radius
- Nutze `locations.json`-Aliasse für "daheim", "kit", "arbeit", etc.
- `config/` ist privat (`.gitignore`) — nie echte Koordinaten oder Keys committen

## Dependencies
- Python 3, `requests`
- `config/serpapi.env` mit gültigem Key
- `config/locations.json` mit Orts-Aliassen

## Location Aliases
- `kit` → KIT Campus Süd (muss in `locations.json` hinterlegt sein)
- `home` → Privatadresse (muss in `locations.json` hinterlegt sein)
- Agent fragt bei unbekanntem Alias nach Koordinaten
