import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_DATA_GOV_KEY")

CITIES = [
    {"name": "Harrisburg PA", "city": "Harrisburg", "state": "PA"},
    {"name": "Harrisburg NC", "city": "Harrisburg", "state": "NC"},
    {"name": "New York NY",   "city": "New York",   "state": "NY"},
    {"name": "Austin TX",     "city": "Austin",     "state": "TX"},
    {"name": "Chicago IL",    "city": "Chicago",    "state": "IL"},
]

STATE_FIPS = {
    "PA": "42",
    "NC": "37",
    "NY": "36",
    "TX": "48",
    "IL": "17"
}

def fetch_crime(city):
    """Fetch crime data for a city using FBI Crime Data API"""
    state_fips = STATE_FIPS.get(city["state"])
    
    url = (
        f"https://api.usa.gov/crime/fbi/cde/arrest/state/{state_fips}/all"
        f"?from=2019&to=2022&API_KEY={API_KEY}"
    )
    
    response = requests.get(url)
    
    if response.status_code != 200:
        raise ValueError(f"API error for {city['name']}: {response.status_code}")
    
    data = response.json()
    
    # Extract total arrests across all years
    total_arrests = 0
    years_found = 0
    
    if "data" in data:
        for entry in data["data"]:
            if "Total" in entry:
                total_arrests += entry["Total"]
                years_found += 1
    
    avg_annual_arrests = round(total_arrests / years_found, 2) if years_found > 0 else 0
    
    return {
        "city":                 city["name"],
        "state":                city["state"],
        "avg_annual_arrests":   avg_annual_arrests,
        "years_measured":       years_found,
        "ingested_at":          datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def run():
    print("Starting crime data ingestion...\n")
    records = []
    errors  = []

    for city in CITIES:
        print(f"  Fetching {city['name']}...")
        try:
            record = fetch_crime(city)
            records.append(record)
            print(f"  Done — avg annual arrests: {record['avg_annual_arrests']}")
        except ValueError as e:
            print(f"  ERROR: {e}")
            errors.append(city["name"])

    if records:
        df = pd.DataFrame(records)
        df.to_csv("raw/crime.csv", index=False)
        print(f"\nDone! Saved {len(df)} records to raw/crime.csv")
        print(df.to_string(index=False))

    if errors:
        print(f"\nFailed cities: {errors}")


if __name__ == "__main__":
    run()