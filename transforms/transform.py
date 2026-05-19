import sqlite3
import pandas as pd

def run():
    conn = sqlite3.connect("feature_store/localpulse.db")

    # Load updated raw CSV into SQLite
    df = pd.read_csv("raw/weather.csv")
    df.to_sql("raw_weather", conn, if_exists="replace", index=False)
    print("Loaded raw data into database")

    # SQL transformation - engineer new features
    query = """
        SELECT
            city,
            state,
            lat,
            lon,
            avg_max_temp_f,
            avg_min_temp_f,
            avg_temp_f,
            temp_range_f,
            total_precipitation,

            -- Engineered features
            CASE
                WHEN avg_temp_f > 85 THEN 'hot'
                WHEN avg_temp_f > 70 THEN 'warm'
                WHEN avg_temp_f > 55 THEN 'mild'
                ELSE 'cold'
            END AS temp_category,

            CASE
                WHEN total_precipitation > 20 THEN 'wet'
                WHEN total_precipitation > 5  THEN 'moderate'
                ELSE 'dry'
            END AS precipitation_category,

            CASE
                WHEN temp_range_f > 30 THEN 'high variability'
                WHEN temp_range_f > 15 THEN 'moderate variability'
                ELSE 'stable'
            END AS temp_stability,

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