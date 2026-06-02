import sys
import os

# Ensure the project root is on the path so imports work regardless of
# which directory the script is called from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
from feature_store.data_quality import run_quality_checks


def run():
    conn = sqlite3.connect("feature_store/localpulse.db")

    # ── Load all raw CSVs into SQLite ──────────────────────────────
    weather_df = pd.read_csv("raw/weather.csv")
    crime_df   = pd.read_csv("raw/crime.csv")
    schools_df = pd.read_csv("raw/schools.csv")

    weather_df.to_sql("raw_weather", conn, if_exists="replace", index=False)
    crime_df.to_sql("raw_crime",     conn, if_exists="replace", index=False)
    schools_df.to_sql("raw_schools", conn, if_exists="replace", index=False)
    print("Loaded all raw data into database")

    # ── Weather features ───────────────────────────────────────────
    weather_query = """
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

    # ── Crime features ─────────────────────────────────────────────
    crime_query = """
        SELECT
            state,
            state_name,
            violent_crime_rate,
            property_crime_rate,
            safety_index,
            safety_category
        FROM raw_crime
    """

    # ── School features ────────────────────────────────────────────
    schools_query = """
        SELECT
            state,
            state_name,
            total_schools,
            total_enrollment,
            avg_school_enrollment,
            student_teacher_ratio,
            education_score,
            education_category
        FROM raw_schools
    """

    # ── Build each feature table ───────────────────────────────────
    weather_features = pd.read_sql_query(weather_query,  conn)
    crime_features   = pd.read_sql_query(crime_query,    conn)
    schools_features = pd.read_sql_query(schools_query,  conn)

    weather_features.to_sql("weather_features", conn, if_exists="replace", index=False)
    crime_features.to_sql("crime_features",     conn, if_exists="replace", index=False)
    schools_features.to_sql("school_features",  conn, if_exists="replace", index=False)
    print("Feature tables created")

    # ── Master joined feature table ────────────────────────────────
    master_query = """
        SELECT
            w.city,
            w.state,
            w.avg_temp_f,
            w.temp_range_f,
            w.total_precipitation,
            w.temp_category,
            w.precipitation_category,
            w.temp_stability,
            c.violent_crime_rate,
            c.property_crime_rate,
            c.safety_index,
            c.safety_category,
            s.total_schools,
            s.student_teacher_ratio,
            s.education_score,
            s.education_category
        FROM weather_features w
        LEFT JOIN crime_features  c ON w.state = c.state
        LEFT JOIN school_features s ON w.state = s.state
    """

    master_df = pd.read_sql_query(master_query, conn)
    master_df.to_sql("master_features", conn, if_exists="replace", index=False)
    print("Master feature table created")

    # ── Liveability Score ──────────────────────────────────────────
    liveability_query = """
        SELECT
            city,
            state,
            avg_temp_f,
            temp_range_f,
            total_precipitation,
            temp_category,
            precipitation_category,
            temp_stability,
            violent_crime_rate,
            property_crime_rate,
            safety_index,
            safety_category,
            total_schools,
            student_teacher_ratio,
            education_score,
            education_category,

            -- Liveability score built entirely in SQL
            MIN(100, MAX(0,
                50

                -- Weather points
                + CASE temp_category
                    WHEN 'warm' THEN 15
                    WHEN 'mild' THEN 10
                    WHEN 'hot'  THEN -10
                    WHEN 'cold' THEN -15
                    ELSE 0 END

                + CASE precipitation_category
                    WHEN 'moderate' THEN 10
                    WHEN 'dry'      THEN 5
                    WHEN 'wet'      THEN -10
                    ELSE 0 END

                + CASE temp_stability
                    WHEN 'stable'               THEN 10
                    WHEN 'moderate variability' THEN 5
                    WHEN 'high variability'     THEN -5
                    ELSE 0 END

                -- Safety points
                + CASE safety_category
                    WHEN 'safe'       THEN 20
                    WHEN 'moderate'   THEN 10
                    WHEN 'high crime' THEN -30
                    ELSE 0 END

                -- Education points
                + CASE education_category
                    WHEN 'excellent' THEN 20
                    WHEN 'good'      THEN 10
                    WHEN 'average'   THEN 5
                    WHEN 'poor'      THEN -10
                    ELSE 0 END

            )) AS liveability_score

        FROM master_features
        ORDER BY liveability_score DESC
    """

    liveability_df = pd.read_sql_query(liveability_query, conn)
    liveability_df.to_sql("liveability_features", conn, if_exists="replace", index=False)

    print("\nLiveability scores:")
    print(liveability_df[["city", "safety_category", "education_category",
                           "temp_category", "liveability_score"]].to_string(index=False))

    conn.close()
    print("\nAll transforms complete!")

    # Run data quality checks now that all feature tables are built.
    # If anything critical is wrong (missing columns, nulls, out-of-range values)
    # this will print a full report and raise an exception so the pipeline
    # stops loudly instead of silently producing bad data.
    run_quality_checks()


if __name__ == "__main__":
    run()