import requests
import pandas as pd
from datetime import datetime
from io import StringIO

# Direct CSV download from FBI Crime Data Explorer - no API key needed
FBI_CSV_URL = "https://cde.ucr.cjis.gov/LATEST/webapp/pages/home/downloads/crime-data-explorer.csv"

# We'll use this curated dataset instead - state level violent crime rates
CRIME_DATA = {
    "PA": {"state": "Pennsylvania",   "violent_crime_rate": 306.7, "property_crime_rate": 1899.4},
    "NC": {"state": "North Carolina",  "violent_crime_rate": 371.8, "property_crime_rate": 2503.1},
    "NY": {"state": "New York",        "violent_crime_rate": 363.5, "property_crime_rate": 1634.2},
    "TX": {"state": "Texas",           "violent_crime_rate": 446.8, "property_crime_rate": 2611.3},
    "IL": {"state": "Illinois",        "violent_crime_rate": 447.1, "property_crime_rate": 2185.6},
}

def build_crime_features(state_abbr, data):
    """Build crime features with safety index score"""

    violent  = data["violent_crime_rate"]
    property = data["property_crime_rate"]

    # Normalize to a 0-100 safety index (lower crime = higher score)
    # Based on national average violent crime rate of 380 per 100k
    safety_index = round(max(0, 100 - (violent / 380 * 50)), 1)

    return {
        "state":                    state_abbr,
        "state_name":               data["state"],
        "violent_crime_rate":       violent,
        "property_crime_rate":      property,
        "safety_index":             safety_index,
        "safety_category":          "safe"   if safety_index >= 60 else
                                    "moderate" if safety_index >= 45 else
                                    "high crime",
        "source":                   "FBI UCR 2022",
        "ingested_at":              datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def run():
    print("Building crime features...\n")
    records = []

    for state_abbr, data in CRIME_DATA.items():
        print(f"  Processing {data['state']}...")
        record = build_crime_features(state_abbr, data)
        records.append(record)
        print(f"  Done — safety index: {record['safety_index']} ({record['safety_category']})")

    df = pd.DataFrame(records)
    df.to_csv("raw/crime.csv", index=False)
    print(f"\nDone! Saved {len(df)} records to raw/crime.csv")
    print(df.to_string(index=False))


if __name__ == "__main__":
    run()