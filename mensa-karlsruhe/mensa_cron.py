#!/usr/bin/env python3
"""
Mensa Cron Formatter — konsistente Ausgabe für WhatsApp
Ruft die Mensa-API ab und formatiert den Plan kompakt.
"""

import json
import subprocess
import sys
from datetime import date, datetime

CANTEEN = "adenauerring"
API_BASE = "https://mensa-api.fnka.de"

# Linie-Mapping: ID -> Anzeigename
LINE_NAMES = {
    "l1": "Linie 1",
    "l2": "Linie 2",
    "l3": "Linie 3",
    "l45": "Linie 4",
    "l5": "Linie 5",
    "schnitzelbar": "Schnitzelbar",
    "update": "Linie 6",
    "abend": "Abend",
    "aktion": "[kœri]werk",
    "heisstheke": "Cafeteria",
    "pizza": "[pizza]werk",
    "salat_dessert": "Salate / Vorspeisen",
}

# Linien, die wir anzeigen (Reihenfolge)
ACTIVE_LINES = [
    "l1", "l2", "l3", "l45", "l5",
    "schnitzelbar", "update", "abend",
    "aktion", "heisstheke", "pizza", "salat_dessert",
]


def api_get(path: str) -> dict:
    url = f"{API_BASE}{path}"
    result = subprocess.run(
        ["curl", "-s", "-L", "--max-time", "15", url],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def fmt_price(p: str) -> str:
    return p.replace("\u20ac", "€").strip() if p else ""


def fmt_meal(meal: dict, omit_price: bool = False) -> str:
    name = meal.get("name", "").strip()
    price = fmt_price(meal.get("price", ""))
    cl = meal.get("classifiers", [])

    # Markierungen
    tags = ""
    if "VEG" in cl or "V" in cl:
        tags += " 🌿"
    elif "VG" in cl:
        tags += " 🌿"

    # Info-Linien wie "zu jedem Gericht..." kürzer fassen
    if "zu jedem gericht" in name.lower():
        return None  # Skippen, ist nur Info

    if price and not omit_price:
        return f"• {name}{tags} — {price}"
    return f"• {name}{tags}"


def fmt_line(line: dict) -> str:
    line_id = line.get("id", "")
    if line_id not in ACTIVE_LINES:
        return None

    meals = line.get("meals", [])
    if not meals:
        return None

    # GESCHLOSSEN filtern
    if len(meals) == 1 and meals[0].get("name", "").strip().upper() == "GESCHLOSSEN":
        return None

    display_name = LINE_NAMES.get(line_id, line.get("name", line_id))

    # Preis-Zusammenfassung pro Linie wenn alle gleich
    prices = [fmt_price(m.get("price", "")) for m in meals if fmt_price(m.get("price", ""))]
    unique_prices = [p for p in prices if p]
    if unique_prices and len(set(unique_prices)) == 1 and line_id not in ("schnitzelbar", "update", "aktion", "pizza"):
        header = f"**{display_name}** — {unique_prices[0]}"
        # Preise aus Einzelzeilen entfernen, da schon im Header
        formatted_meals = []
        for m in meals:
            fm = fmt_meal(m, omit_price=True)
            if fm:
                formatted_meals.append(fm)
    else:
        header = f"**{display_name}**"
        formatted_meals = []
        for m in meals:
            fm = fmt_meal(m)
            if fm:
                formatted_meals.append(fm)

    if not formatted_meals:
        return None

    return header + "\n" + "\n".join(formatted_meals)


def get_plan(target_date: date = None) -> str:
    if target_date is None:
        target_date = date.today()

    dstr = target_date.isoformat()
    data = api_get(f"/plans/{dstr}?canteens={CANTEEN}")

    if not data.get("success"):
        raise RuntimeError(f"API error: {data}")

    canteen_data = data["data"][0]
    lines = canteen_data.get("lines", [])

    # Datum formatieren
    weekday = datetime.now().strftime("%A")
    weekdays_de = {
        "Monday": "Montag", "Tuesday": "Dienstag", "Wednesday": "Mittwoch",
        "Thursday": "Donnerstag", "Friday": "Freitag", "Saturday": "Samstag", "Sunday": "Sonntag"
    }
    weekday_de = weekdays_de.get(weekday, weekday)
    date_str = target_date.strftime("%d.%m.%Y")

    header = f"🍽️ *Mensa am Adenauerring — {weekday_de}, {date_str}*\n"

    parts = []
    for lid in ACTIVE_LINES:
        for line in lines:
            if line.get("id") == lid:
                part = fmt_line(line)
                if part:
                    parts.append(part)
                break

    if not parts:
        return header + "\nHeute leider kein Plan verfügbar."

    return header + "\n\n" + "\n\n".join(parts)


if __name__ == "__main__":
    try:
        print(get_plan())
    except Exception as e:
        print(f"❌ Fehler beim Laden des Mensa-Plans: {e}", file=sys.stderr)
        sys.exit(1)
