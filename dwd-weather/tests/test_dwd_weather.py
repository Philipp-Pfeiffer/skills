import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dwd_stations import (
    haversine,
    get_station_by_id,
    find_nearest_station,
    search_stations,
    resolve_location,
    geocode_location,
)
from dwd_forecast import format_forecast, format_warnings, _fetch_json


# --- Station tests ---

def test_haversine():
    # Karlsruhe to Stuttgart
    d = haversine(49.0373, 8.3637, 48.7758, 9.1829)
    assert 60 < d < 70


def test_get_station_by_id_known():
    s = get_station_by_id("10727")
    assert s is not None
    assert s["name"] == "KARLSRUHE"
    assert s["id"] == "10727"


def test_get_station_by_id_unknown():
    s = get_station_by_id("FAKE99")
    assert s is None


def test_search_stations_karlsruhe():
    results = search_stations("Karlsruhe")
    assert len(results) >= 1
    ids = [r["id"] for r in results]
    assert "10727" in ids


def test_search_stations_berlin():
    results = search_stations("Berlin")
    assert len(results) >= 1
    ids = [r["id"] for r in results]
    assert "G005" in ids


def test_search_stations_no_match():
    results = search_stations("XYZNONEXISTENT")
    assert len(results) == 0


def test_find_nearest_station_karlsruhe():
    # Coordinates near Karlsruhe center
    s = find_nearest_station(49.03, 8.37)
    assert s is not None
    assert s["id"] in ("10727", "Q208")
    assert s["distance_km"] < 10


def test_resolve_location_by_id():
    r = resolve_location("10727")
    assert r is not None
    assert r["matched_by"] == "id"
    assert r["id"] == "10727"


def test_resolve_location_by_name():
    r = resolve_location("Karlsruhe")
    assert r is not None
    assert r["matched_by"] == "name"
    assert r["id"] in ("10727", "Q208")


@pytest.mark.network
def test_resolve_location_by_geocode():
    r = resolve_location("Buxtehude")
    assert r is not None
    assert r["matched_by"] == "geocode"
    # Buxtehude is near Hamburg, should get a Hamburg-area station
    assert r["distance_km"] < 50


@pytest.mark.network
def test_geocode_location():
    geo = geocode_location("Karlsruhe")
    assert geo is not None
    assert 48.9 < geo["lat"] < 49.1
    assert 8.2 < geo["lon"] < 8.5


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
                "descriptionText": "Von Sueden ziehen Gewitter auf.",
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


@pytest.mark.network
def test_live_forecast_by_city_name():
    from dwd_forecast import get_forecast
    r = resolve_location("Karlsruhe")
    assert r is not None
    data = get_forecast(r["id"])
    assert "error" not in data
    assert "daily" in data
    assert len(data["daily"]) > 0
