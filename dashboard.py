import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = "feature_store/localpulse.db"


def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM liveability_features ORDER BY liveability_score DESC", conn
    )
    conn.close()
    return df


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="LocalPulse", page_icon="🏙️", layout="wide")
st.title("🏙️ LocalPulse — City Liveability Dashboard")
st.caption("Live weather · FBI crime data · School quality · Composite liveability scores")

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data: {e}\n\nRun the pipeline first: `python transforms/transform.py`")
    st.stop()  # halt rendering — nothing else will display if db is missing

# ── Section 1: Leaderboard ────────────────────────────────────────────────────
st.header("City Leaderboard")
st.write("All cities ranked by composite liveability score (0–100).")

leaderboard_cols = [
    "city", "state", "liveability_score",
    "safety_category", "education_category", "temp_category"
]

# hide the dataframe index since it adds no value here
st.dataframe(
    df[leaderboard_cols].reset_index(drop=True),
    width="stretch"
)

# ── Section 2: Bar chart ──────────────────────────────────────────────────────
st.header("Liveability Score Comparison")
st.write("Visual breakdown of scores across all cities.")

# st.bar_chart expects the column to plot as values and the index as labels
chart_df = df[["city", "liveability_score"]].set_index("city")
st.bar_chart(chart_df, width="stretch")

# ── Section 3: City deep dive ─────────────────────────────────────────────────
st.header("City Deep Dive")
st.write("Select a city to see all individual features.")

selected_city = st.selectbox(
    "Choose a city",
    options=df["city"].tolist()
)

city_row = df[df["city"] == selected_city].iloc[0]

# Split the features into three themed columns so the layout isn't one long list
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Weather")
    st.metric("Avg Temp (°F)",        city_row["avg_temp_f"])
    st.metric("Temp Range (°F)",      city_row["temp_range_f"])
    st.metric("Total Precipitation",  city_row["total_precipitation"])
    st.metric("Temp Category",        city_row["temp_category"])
    st.metric("Precipitation",        city_row["precipitation_category"])
    st.metric("Temp Stability",       city_row["temp_stability"])

with col2:
    st.subheader("Safety")
    st.metric("Safety Index",         city_row["safety_index"])
    st.metric("Safety Category",      city_row["safety_category"])
    st.metric("Violent Crime Rate",   city_row["violent_crime_rate"])
    st.metric("Property Crime Rate",  city_row["property_crime_rate"])

with col3:
    st.subheader("Education")
    st.metric("Education Score",      city_row["education_score"])
    st.metric("Education Category",   city_row["education_category"])
    st.metric("Student/Teacher Ratio",city_row["student_teacher_ratio"])
    st.metric("Total Schools",        city_row["total_schools"])

# Liveability score displayed prominently at the bottom
st.divider()
st.metric(
    label=f"Liveability Score — {selected_city}",
    value=city_row["liveability_score"],
    help="Composite score (0–100) based on weather, safety, and education."
)
