import requests
import pandas as pd
from datetime import datetime

# Free, no API key needed
CITIES = ["New York", "Austin", "Chicago", "Miami", "Seattle"]

def fetch_weather(city):
    # Using Open-Meteo - completely free, no sign up
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo = requests.get(url).json()
    
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]
    
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&forecast_days=7"
    weather = requests.get(weather_url).json()
    
    return {
        "city": city,
        "lat": lat,
        "lon": lon,
        "avg_max_temp": sum(weather["daily"]["temperature_2m_max"]) / 7,
        "avg_min_temp": sum(weather["daily"]["temperature_2m_min"]) / 7,
        "total_precipitation": sum(weather["daily"]["precipitation_sum"]),
        "ingested_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def run():
    print("Starting ingestion...")
    records = []
    
    for city in CITIES:
        print(f"  Fetching {city}...")
        record = fetch_weather(city)
        records.append(record)
    
    df = pd.DataFrame(records)
    df.to_csv("raw/weather.csv", index=False)
    print(f"\nDone! Saved {len(df)} records to raw/weather.csv")
    print(df)

if __name__ == "__main__":
    run()