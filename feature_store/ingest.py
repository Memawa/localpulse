import requests
import pandas as pd
from datetime import datetime

CITIES = [
    {"name": "Harrisburg PA", "city": "Harrisburg", "state": "PA", "country": "US"},
    {"name": "Harrisburg NC", "city": "Harrisburg", "state": "NC", "country": "US"},
    {"name": "New York NY",   "city": "New York",   "state": "NY", "country": "US"},
    {"name": "Austin TX",     "city": "Austin",     "state": "TX", "country": "US"},
    {"name": "Chicago IL",    "city": "Chicago",    "state": "IL", "country": "US"},
]

# Map state abbreviations to full names as the API returns them
STATE_MAP = {
    "PA": "pennsylvania",
    "NC": "north carolina",
    "NY": "new york",
    "TX": "texas",
    "IL": "illinois"
}

def get_coordinates(city):
    """Find unambiguous coordinates for a city using state validation"""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city['city']}&count=10"
    response = requests.get(url).json()

    if "results" not in response:
        raise ValueError(f"No results returned for {city['name']}")

    state_full = STATE_MAP.get(city["state"], city["state"].lower())

    result = None
    for r in response["results"]:
        if state_full in r.get("admin1", "").lower():
            result = r
            break

    if not result:
        raise ValueError(f"Could not find unambiguous match for {city['name']}")

    print(f"  Matched {city['name']} → {result['name']}, {result.get('admin1')} ({result['latitude']}, {result['longitude']})")
    
    return result["latitude"], result["longitude"]


def fetch_weather(city):
    """Fetch 7 day weather forecast for a city and return engineered features"""
    lat, lon = get_coordinates(city)

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&forecast_days=7"
        f"&temperature_unit=fahrenheit"
    )

    weather = requests.get(weather_url).json()

    max_temps   = weather["daily"]["temperature_2m_max"]
    min_temps   = weather["daily"]["temperature_2m_min"]
    precip      = weather["daily"]["precipitation_sum"]

    avg_max     = round(sum(max_temps) / len(max_temps), 2)
    avg_min     = round(sum(min_temps) / len(min_temps), 2)
    total_precip = round(sum(precip), 2)

    return {
        "city":               city["name"],
        "state":              city["state"],
        "lat":                lat,
        "lon":                lon,
        "avg_max_temp_f":     avg_max,
        "avg_min_temp_f":     avg_min,
        "avg_temp_f":         round((avg_max + avg_min) / 2, 2),
        "temp_range_f":       round(avg_max - avg_min, 2),
        "total_precipitation": total_precip,
        "ingested_at":        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def run():
    print("Starting ingestion...\n")
    records = []
    errors  = []

    for city in CITIES:
        print(f"  Fetching {city['name']}...")
        try:
            record = fetch_weather(city)
            records.append(record)
        except ValueError as e:
            print(f"  ERROR: {e}")
            errors.append(city["name"])

    if records:
        df = pd.DataFrame(records)
        df.to_csv("raw/weather.csv", index=False)
        print(f"\nDone! Saved {len(df)} records to raw/weather.csv")
        print(df.to_string(index=False))

    if errors:
        print(f"\nFailed cities: {errors}")


if __name__ == "__main__":
    run()