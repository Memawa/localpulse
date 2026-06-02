import sys
import os
import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

DB_PATH = "feature_store/localpulse.db"

app = FastAPI(
    title="LocalPulse API",
    description="Query city liveability features — weather, crime, schools, and composite scores.",
    version="1.0.0"
)


def get_conn():
    return sqlite3.connect(DB_PATH)


@app.get("/cities")
def list_cities():
    """Return all cities available in the feature store."""
    conn = get_conn()
    df = pd.read_sql_query("SELECT DISTINCT city, state FROM liveability_features ORDER BY city", conn)
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail="No cities found. Run the pipeline first.")

    return {"cities": df.to_dict(orient="records")}


@app.get("/features/{city}")
def get_city_features(city: str):
    """Return all features for a specific city (e.g. 'New York NY')."""
    conn = get_conn()
    df = pd.read_sql_query(
        "SELECT * FROM liveability_features WHERE city = ?",
        conn, params=(city,)
    )
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail=f"City '{city}' not found.")

    return {"city": city, "features": df.to_dict(orient="records")[0]}


@app.get("/leaderboard")
def get_leaderboard():
    """Return all cities ranked by liveability score."""
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT city, state, liveability_score, safety_category,
               education_category, temp_category
        FROM liveability_features
        ORDER BY liveability_score DESC
        """,
        conn
    )
    conn.close()

    if df.empty:
        raise HTTPException(status_code=404, detail="No data found. Run the pipeline first.")

    return {"leaderboard": df.to_dict(orient="records")}
