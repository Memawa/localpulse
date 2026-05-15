import sqlite3
import pandas as pd

def run():
    # Connect to (or create) the database
    conn = sqlite3.connect("feature_store/localpulse.db")
    
    # Load raw CSV into SQLite
    df = pd.read_csv("raw/weather.csv")
    df.to_sql("raw_weather", conn, if_exists="replace", index=False)
    print("Loaded raw data into database")

    # SQL transformation - engineer new features
    query = """
        SELECT
            city,
            lat,
            lon,
            avg_max_temp,
            avg_min_temp,
            total_precipitation,
            
            -- Engineered features
            ROUND(avg_max_temp - avg_min_temp, 2)        AS temp_range,
            ROUND((avg_max_temp + avg_min_temp) / 2, 2)  AS avg_temp,
            CASE 
                WHEN total_precipitation > 20 THEN 'wet'
                WHEN total_precipitation > 5  THEN 'moderate'
                ELSE 'dry'
            END                                           AS precipitation_category,
            CASE
                WHEN avg_max_temp > 30 THEN 'hot'
                WHEN avg_max_temp > 20 THEN 'warm'
                WHEN avg_max_temp > 10 THEN 'mild'
                ELSE 'cold'
            END                                           AS temp_category,
            ingested_at

        FROM raw_weather
    """

    features_df = pd.read_sql_query(query, conn)
    features_df.to_sql("weather_features", conn, if_exists="replace", index=False)
    
    print("\nEngineered features saved! Here's a preview:")
    print(features_df.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    run()