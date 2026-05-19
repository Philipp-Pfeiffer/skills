import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dwd_stations import haversine, parse_stations, find_nearest_station, search_stations
from dwd_forecast import format_forecast, format_warnings, _fetch_json

# --- Station tests ---

def test_haversine():
    # Karlsruhe to Stuttgart
    d = haversine(49.0373, 8.3637, 48.7758, 9.1829)
    assert 60 < d < 70

def test_parse_stations():
    raw = b"02522 18760101 20081031            112     49.0373    8.3637 Karlsruhe                                Baden-W\xfcrttemberg                        Frei\n"
    stations = parse_stations(raw)
    assert len(stations) == 1
    assert stations[0]["id"] == "02522"
    assert stations[0]["name"] == "Karlsruhe"
    assert stations[0]["lat"] == 49.0373
    assert stations[0]["lon"] == 8.3637

def test_search_stations():
    raw = b"02522 18760101 20081031 112 49.0373 8.3637 Karlsruhe BW Frei\n06310 20040801 20260519 1 13.8239 54.0 Karlshagen MV Frei\n"
    stations = parse_stations(raw)
    results = search_stations("karlsruhe", stations)
    assert len(results) == 1
    assert results[0]["id"] == "02522"

def test_find_nearest_station():
    raw = b"02522 18760101 20081031 112 49.0373 8.3637 Karlsruhe BW Frei\n10865 19510101 20260519 37 52.5597 13.2877 Berlin-Tegel BE Frei\n"
    stations = parse_stations(raw)
    nearest = find_nearest_station(49.0, 8.4, stations)
    assert nearest["id"] == "02522"

# --- Forecast tests ---

def test_format_forecast_error():
    data = {"error": "Station not found"}
    out = format_forecast(data)
    assert "Error" in out

def test_format_forecast_mock():
    data = {
        "station_id": "10865",
        "forecast_start": "2026-05-19T00:00:00+00:00",
        "daily": [
            {"date": "2026-05-19", "temp_min_c": 8.6, "temp_max_c": 18.1, "precipitation_mm": 5.6},
            {"date": "2026-05-20", "temp_min_c": 11.7, "temp_max_c": 18.3, "precipitation_mm": 0.0},
        ],
        "hourly": [
            {"hour": 0, "temperature_c": 10.0, "rain_mm_h": 0.1, "humidity_pct": 41.7},
            {"hour": 1, "temperature_c": 9.7, "rain_mm_h": 0.0, "humidity_pct": 42.0},
        ],
    }
    out = format_forecast(data, hourly_count=2)
    assert "10865" in out
    assert "18.1" in out
    assert "10.0" in out
    assert "42" in out

# --- Warning tests ---

def test_format_warnings_error():
    data = {"error": "Network timeout"}
    out = format_warnings(data, "gemeinde")
    assert "Error" in out

def test_format_warnings_empty():
    data = {"warnings": []}
    out = format_warnings(data, "gemeinde")
    assert "No active warnings" in out

def test_format_warnings_with_data():
    data = {
        "warnings": [
            {
                "level": 2,
                "event": "GEWITTER",
                "start": 1779197220000,
                "end": 1779202800000,
                "descriptionText": "Von S\xfcden ziehen Gewitter auf.",
            }
        ]
    }
    out = format_warnings(data, "gemeinde")
    assert "GEWITTER" in out
    assert "Moderate" in out

# --- Integration-style tests (require network, skipped by default) ---

@pytest.mark.network
def test_live_forecast():
    from dwd_forecast import get_forecast
    data = get_forecast("10865")
    assert "error" not in data
    assert "daily" in data
    assert len(data["daily"]) > 0

@pytest.mark.network
def test_live_warnings():
    from dwd_forecast import get_warnings
    data = get_warnings("gemeinde")
    assert "error" not in data
