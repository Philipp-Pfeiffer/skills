#!/usr/bin/env python3
"""
dwd_weather_chart.py - Tufte-style Wetter-Visualisierung mit subtilen SVG-Patterns
und Box-Plot Temperatur-Darstellung (Min/Max, Q1, Median, Q3).

Option C: Quartile im Temperatur-Balken + subtile Wetter-Patterns.
"""

import argparse
import json
import os
import subprocess
import urllib.request
from datetime import datetime

# ── Wetter-Icons → Pattern-Typ ────────────────────────────────────
ICON_MAP = {
    1:  "sunny",   # ☀  klar
    2:  "sunny",   # 🌤  leicht bewölkt
    3:  "cloudy",  # ⛅  bewölkt
    4:  "cloudy",  # ☁  stark bewölkt
    5:  "cloudy",  # Nebel
    6:  "rain",    # Sprühregen
    7:  "rain",    # 🌧  Regen
    8:  "rain",    # 🌧  starker Regen
    9:  "rain",    # Eisregen
    10: "rain",    # Schneeregen
    11: "rain",    # Schnee
    12: "rain",    # starker Schneefall
    13: "rain",    # Schneeschauer
    14: "thunder", # ⛈  Regenschauer
    15: "thunder", # ⛈  starker Regenschauer
    16: "thunder", # ⛈  Gewitter
    17: "thunder", # ⛈  starker Gewitterregen
    18: "thunder", # ⛈  Gewitter mit Hagel
    19: "thunder", # ⛈  Gewitter mit starkem Regen und Hagel
}

# ── SVG-Patterns (subtil, 3-8% Opazität) ─────────────────────────
PATTERNS = {
    "sunny": """
    <pattern id="{pid}" patternUnits="userSpaceOnUse" width="40" height="40">
      <circle cx="5"  cy="8"  r="1.2" fill="#d4a574" opacity="0.04"/>
      <circle cx="20" cy="22" r="1.8" fill="#d4a574" opacity="0.04"/>
      <circle cx="35" cy="12" r="1.0" fill="#d4a574" opacity="0.04"/>
      <circle cx="12" cy="32" r="1.5" fill="#d4a574" opacity="0.04"/>
      <circle cx="28" cy="35" r="1.0" fill="#d4a574" opacity="0.04"/>
    </pattern>
    """,
    "cloudy": """
    <pattern id="{pid}" patternUnits="userSpaceOnUse" width="30" height="30">
      <line x1="0" y1="10" x2="30" y2="10" stroke="#8a9aab" stroke-width="0.6" opacity="0.05"/>
      <line x1="0" y1="20" x2="30" y2="20" stroke="#8a9aab" stroke-width="0.6" opacity="0.05"/>
      <line x1="0" y1="25" x2="30" y2="25" stroke="#8a9aab" stroke-width="0.6" opacity="0.04"/>
    </pattern>
    """,
    "rain": """
    <pattern id="{pid}" patternUnits="userSpaceOnUse" width="20" height="20">
      <line x1="5"  y1="2" x2="3"  y2="10" stroke="#6b8299" stroke-width="0.7" opacity="0.06"/>
      <line x1="15" y1="5" x2="13" y2="13" stroke="#6b8299" stroke-width="0.7" opacity="0.06"/>
      <line x1="10" y1="12" x2="8" y2="20" stroke="#6b8299" stroke-width="0.7" opacity="0.06"/>
    </pattern>
    """,
    "thunder": """
    <pattern id="{pid}" patternUnits="userSpaceOnUse" width="18" height="18">
      <line x1="4"  y1="1"  x2="1"  y2="9"  stroke="#4a5568" stroke-width="0.9" opacity="0.08"/>
      <line x1="12" y1="3"  x2="9"  y2="11" stroke="#4a5568" stroke-width="0.9" opacity="0.08"/>
      <line x1="8"  y1="10" x2="5"  y2="18" stroke="#4a5568" stroke-width="0.9" opacity="0.08"/>
      <line x1="16" y1="5"  x2="13" y2="13" stroke="#4a5568" stroke-width="0.9" opacity="0.07"/>
    </pattern>
    """,
}

# ── API ──────────────────────────────────────────────────────────
def fetch_forecast(station_id: str) -> dict:
    url = f"https://app-prod-ws.warnwetter.de/v30/stationOverviewExtended?stationIds={station_id}"
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.load(resp)


# ── Quartile ─────────────────────────────────────────────────────
def quartiles(values):
    s = sorted(values)
    n = len(s)
    # Median
    if n % 2 == 0:
        median = (s[n//2 - 1] + s[n//2]) / 2
    else:
        median = s[n//2]
    # Q1: Median der unteren Hälfte
    lower = s[:n//2]
    if len(lower) % 2 == 0 and len(lower) > 0:
        q1 = (lower[len(lower)//2 - 1] + lower[len(lower)//2]) / 2
    elif len(lower) > 0:
        q1 = lower[len(lower)//2]
    else:
        q1 = s[0]
    # Q3: Median der oberen Hälfte
    upper = s[(n+1)//2:]
    if len(upper) % 2 == 0 and len(upper) > 0:
        q3 = (upper[len(upper)//2 - 1] + upper[len(upper)//2]) / 2
    elif len(upper) > 0:
        q3 = upper[len(upper)//2]
    else:
        q3 = s[-1]
    return s[0], q1, median, q3, s[-1]


# ── SVG Builder ───────────────────────────────────────────────────
def build_svg(data: dict, station_name: str = "") -> str:
    root = data[list(data.keys())[0]]
    days_data = root.get("days", [])
    forecast1 = root.get("forecast1", {})

    # Stündliche Temperaturen und Zeitstempel
    hourly_temps = [t / 10.0 for t in forecast1.get("temperature", [])]
    start_ms = forecast1.get("start", 0)
    timestep_ms = forecast1.get("timeStep", 3600000)

    if not hourly_temps:
        raise ValueError("Keine stündlichen Temperaturdaten")

    # Tagesgrenzen: wir haben 24h pro Tag, aber forecast1 startet zu einer bestimmten Zeit.
    # Wir nehmen an, dass die ersten 24h = Tag 0, nächste 24h = Tag 1, etc.
    # Bessere Herangehensweise: Zeitstempel aus start_ms berechnen und auf Tage mappen.
    from datetime import timezone
    start_dt = datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc)

    # Mappe stündliche Werte zu Tagesindex (0 = erster Tag in Daten)
    temps_per_day = {}
    for i, t in enumerate(hourly_temps):
        ts = start_ms + i * timestep_ms
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        day_key = dt.strftime("%Y-%m-%d")
        if day_key not in temps_per_day:
            temps_per_day[day_key] = []
        temps_per_day[day_key].append(t)

    # Wir nehmen die ersten 5 Tage aus `days_data`
    days = days_data[:5]

    # Layout
    CARD_W = 132
    GAP = 14
    MARGIN = 36
    W = MARGIN * 2 + len(days) * CARD_W + (len(days) - 1) * GAP
    H = 360

    # Titel position - immer anpassen damit es nicht abgeschnitten wird

    # Globale Temperatur-Skala aus stündlichen Daten (alle Tage)
    all_temps = []
    for d in days:
        dk = d.get("dayDate")
        if dk in temps_per_day:
            all_temps.extend(temps_per_day[dk])
    if all_temps:
        global_min = min(all_temps) - 3
        global_max = max(all_temps) + 3
    else:
        # Fallback auf daily min/max
        global_min = min(d.get("temperatureMin", 0) / 10.0 for d in days) - 3
        global_max = max(d.get("temperatureMax", 0) / 10.0 for d in days) + 3

    weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

    defs = []
    cards = []

    for i, day in enumerate(days):
        x = MARGIN + i * (CARD_W + GAP)
        icon_id = day.get("icon", 1)
        ptype = ICON_MAP.get(icon_id, "cloudy")
        pid = f"p-{ptype}-{i}"

        # Pattern in defs
        defs.append(PATTERNS[ptype].replace("{pid}", pid))

        date_str = day.get("dayDate", "?")
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekday_label = weekday_names[dt.weekday()]
        date_label = f"{dt.day:02d}.{dt.month:02d}."

        tmin = day.get("temperatureMin", 0) / 10.0
        tmax = day.get("temperatureMax", 0) / 10.0
        rain_prob = day.get("precipitationProbablity", 0)
        if rain_prob is None:
            rain_prob = 0
        rain_prob = int(rain_prob / 10.0)
        rain_mm = day.get("precipitation", 0) / 10.0
        wind = day.get("windSpeed", 0) / 10.0
        gust = day.get("windGust", 0) / 10.0
        sun_h = day.get("sunshine", 0) / 10.0 / 60.0

        # Stündliche Daten für diesen Tag
        dk = day.get("dayDate")
        day_hourly = temps_per_day.get(dk, [])

        if len(day_hourly) >= 4:
            q_min, q1, median, q3, q_max = quartiles(day_hourly)
        else:
            q_min, q1, median, q3, q_max = tmin, tmin, (tmin+tmax)/2, tmax, tmax

        # Temperatur-Balken
        bar_y = 170
        bar_h = 18
        bar_w = CARD_W - 24
        bar_x = x + 12

        def t_pos(t):
            return bar_x + max(0, min(bar_w, ((t - global_min) / (global_max - global_min)) * bar_w))

        # Karte
        card = f"""
        <g>
          <!-- Hintergrund + Pattern -->
          <rect x="{x}" y="40" width="{CARD_W}" height="{H-48}" rx="4" fill="#faf9f6" stroke="#ddd" stroke-width="0.5"/>
          <rect x="{x}" y="40" width="{CARD_W}" height="{H-48}" rx="4" fill="url(#{pid})"/>

          <!-- Wochentag -->
          <text x="{x + CARD_W/2}" y="68" text-anchor="middle" font-size="15" fill="#111" font-weight="normal" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{weekday_label}</text>
          <text x="{x + CARD_W/2}" y="86" text-anchor="middle" font-size="11" fill="#999" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{date_label}</text>

          <!-- Temperatur-Box-Plot -->
          <rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" fill="#eee" rx="2"/>
        """

        # Box: Q1-Q3
        x_q1 = t_pos(q1)
        x_q3 = t_pos(q3)
        box_w = max(2, x_q3 - x_q1)
        card += f'  <rect x="{x_q1:.1f}" y="{bar_y+2}" width="{box_w:.1f}" height="{bar_h-4}" fill="#e94560" opacity="0.35" rx="1"/>\n'

        # Median
        x_med = t_pos(median)
        card += f'  <line x1="{x_med:.1f}" y1="{bar_y}" x2="{x_med:.1f}" y2="{bar_y+bar_h}" stroke="#111" stroke-width="1.5"/>\n'

        # Whisker: Min/Max
        x_qmin = t_pos(q_min)
        x_qmax = t_pos(q_max)
        # Nur zeichnen wenn außerhalb der Box
        if x_qmin < x_q1 - 1:
            card += f'  <line x1="{x_qmin:.1f}" y1="{bar_y+bar_h/2}" x2="{x_q1:.1f}" y2="{bar_y+bar_h/2}" stroke="#4a90d9" stroke-width="0.8" stroke-dasharray="2,1"/>\n'
            card += f'  <circle cx="{x_qmin:.1f}" cy="{bar_y+bar_h/2}" r="1.8" fill="#4a90d9"/>\n'
        if x_qmax > x_q3 + 1:
            card += f'  <line x1="{x_q3:.1f}" y1="{bar_y+bar_h/2}" x2="{x_qmax:.1f}" y2="{bar_y+bar_h/2}" stroke="#e94560" stroke-width="0.8" stroke-dasharray="2,1"/>\n'
            card += f'  <circle cx="{x_qmax:.1f}" cy="{bar_y+bar_h/2}" r="1.8" fill="#e94560"/>\n'

        # Temperatur-Labels
        card += f'  <text x="{bar_x}" y="{bar_y+bar_h+16}" font-size="9" fill="#4a90d9" text-anchor="start" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{q_min:.0f}°</text>\n'
        card += f'  <text x="{bar_x+bar_w}" y="{bar_y+bar_h+16}" font-size="9" fill="#e94560" text-anchor="end" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{q_max:.0f}°</text>\n'
        card += f'  <text x="{x_med:.1f}" y="{bar_y+bar_h+28}" font-size="9" fill="#111" text-anchor="middle" font-weight="bold" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">med {median:.0f}°</text>\n'

        # Regenwahrscheinlichkeit entfernt — mm-Anzeige existiert bereits unten
        # rain_bar_y = bar_y + bar_h + 44
        # rain_bar_w = bar_w * (rain_prob / 100.0)
        # card += f'  <text x="{x + CARD_W/2}" y="{rain_bar_y}" text-anchor="middle" font-size="10" fill="#6b8299" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">Regen {rain_prob}%</text>\n'
        # card += f'  <rect x="{bar_x}" y="{rain_bar_y+6}" width="{bar_w}" height="3" rx="1.5" fill="#eee"/>\n'
        # card += f'  <rect x="{bar_x}" y="{rain_bar_y+6}" width="{max(0, rain_bar_w)}" height="3" rx="1.5" fill="#6b8299" opacity="0.6"/>\n'

        # Detail-Block direkt unter dem Temperatur-Balken
        detail_y = bar_y + bar_h + 48
        card += f'  <text x="{x + CARD_W/2}" y="{detail_y}" text-anchor="middle" font-size="10" fill="#d4a574" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">Sonne {sun_h:.1f} h</text>\n'
        card += f'  <text x="{x + CARD_W/2}" y="{detail_y+16}" text-anchor="middle" font-size="10" fill="#8a9aab" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{wind:.0f} km/h (Böen {gust:.0f})</text>\n'
        card += f'  <text x="{x + CARD_W/2}" y="{detail_y+32}" text-anchor="middle" font-size="10" fill="#6b8299" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">{rain_mm:.1f} mm</text>\n'

        card += "</g>\n"
        cards.append(card)

    # Titel
    title_text = station_name if station_name else "Wettervorhersage"

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="ET-Book, ET-Bembo, Palatino, Georgia, serif">',
        '<defs>',
        '\n'.join(defs),
        '</defs>',
        '<rect width="100%" height="100%" fill="#fff"/>',
    ] + cards + [
        f'<text x="{MARGIN}" y="18" font-size="17" fill="#111" font-weight="normal">{title_text}</text>',
        f'<text x="{MARGIN}" y="34" font-size="10" fill="#999">Daten: Deutscher Wetterdienst (DWD)</text>',
        '</svg>',
    ]

    return '\n'.join(svg_parts)


# ── Station-Name (einfache Heuristik) ──────────────────────────────
def resolve_station_name(station_id: str) -> str:
    skill_dir = os.path.dirname(os.path.abspath(__file__))
    stations_file = os.path.join(skill_dir, "mosmix_stations.json")
    try:
        with open(stations_file) as f:
            st = json.load(f)
        for s in st:
            if str(s.get("id")) == station_id or str(s.get("stationId")) == station_id:
                return s.get("name", "")
    except Exception:
        pass
    return ""


# ── Main ──────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Wetter-Chart als Tufte-Style SVG/PNG")
    parser.add_argument("station", help="MOSMIX Stations-ID (z.B. 10865)")
    parser.add_argument("--out", "-o", default="/tmp/weather_chart.png", help="Ausgabepfad (PNG)")
    parser.add_argument("--name", "-n", default="", help="Stations-Name für Titel")
    args = parser.parse_args()

    data = fetch_forecast(args.station)
    name = args.name or resolve_station_name(args.station)
    svg = build_svg(data, name)

    svg_path = args.out.replace(".png", ".svg")
    with open(svg_path, "w") as f:
        f.write(svg)

    subprocess.run(["rsvg-convert", "-w", "900", svg_path, "-o", args.out], check=True)
    print(f"PNG: {args.out}")
    print(f"SVG: {svg_path}")


if __name__ == "__main__":
    main()
