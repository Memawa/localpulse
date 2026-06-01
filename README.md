# LocalPulse 🏙️
### A Neighborhood Feature Store built with Python and SQL

A production-style data engineering project that ingests live weather, 
crime, and school quality data across US cities, engineers ML-ready 
features using SQL, and serves them through a versioned Python interface.

---

## What It Does

LocalPulse simulates the kind of infrastructure real ML teams depend on — 
a reliable, versioned source of clean features that any downstream model 
or analyst can query without re-engineering the pipeline themselves.

Every time the pipeline runs it:
1. Pulls live data from 3 public sources via REST APIs
2. Cleans and transforms raw data into engineered features using SQL
3. Joins all sources into a master feature table
4. Scores each city on liveability using a composite SQL model
5. Stores everything in a versioned feature registry

---

## Architecture
[Public APIs / Data Sources]
↓
[Ingestion Layer]         — feature_store/ingest.py
[                ]         — feature_store/ingest_crime.py
[                ]         — feature_store/ingest_schools.py
↓
[Transformation Layer]    — transforms/transform.py
↓
[Feature Store / Registry] — feature_store/feature_store.py
↓
[Demo Notebook]           — notebooks/demo.ipynb

---

## Data Sources

| Source | Data | Cost |
|---|---|---|
| Open-Meteo API | Live 7-day weather forecast | Free, no key |
| FBI UCR 2022 | State level violent and property crime rates | Free |
| Urban Institute Education Data Portal | School count, enrollment, student/teacher ratio | Free, no key |

---

## Feature Registry (13 Features)

| Feature | Description | Source |
|---|---|---|
| `avg_temp_f` | Average temperature in Fahrenheit | Weather |
| `temp_range_f` | Difference between max and min temp | Weather |
| `temp_category` | Hot / warm / mild / cold label | Weather |
| `precipitation_category` | Wet / moderate / dry label | Weather |
| `temp_stability` | High / moderate / stable variability | Weather |
| `violent_crime_rate` | Violent crimes per 100k people | Crime |
| `property_crime_rate` | Property crimes per 100k people | Crime |
| `safety_index` | Safety score 0-100 | Crime |
| `safety_category` | Safe / moderate / high crime label | Crime |
| `student_teacher_ratio` | Students per teacher | Schools |
| `education_score` | Education quality score 0-100 | Schools |
| `education_category` | Excellent / good / average / poor label | Schools |
| `liveability_score` | Composite city liveability score 0-100 | All sources |

---

## Project Structure
localpulse/
│
├── raw/                        ← downloaded data CSVs
├── transforms/
│   └── transform.py            ← SQL feature engineering
├── feature_store/
│   ├── feature_store.py        ← FeatureStore Python class
│   ├── ingest.py               ← weather ingestion
│   ├── ingest_crime.py         ← crime data ingestion
│   └── ingest_schools.py       ← school data ingestion
├── notebooks/
│   └── demo.ipynb              ← Jupyter demo notebook
├── .env                        ← API keys (never committed)
├── .gitignore
├── requirements.txt
└── README.md

---

## How To Run

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/localpulse.git
cd localpulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.env` file in the root folder:
API_DATA_GOV_KEY=your_key_here

### 4. Run the full pipeline
```bash
# Ingest all data sources
python feature_store/ingest.py
python feature_store/ingest_crime.py
python feature_store/ingest_schools.py

# Transform and build feature tables
python transforms/transform.py

# Register all features
python feature_store/feature_store.py
```

### 5. Open the demo notebook
```bash
jupyter notebook
```
Navigate to `notebooks/demo.ipynb` and run all cells.

---

## Querying the Feature Store

```python
from feature_store.feature_store import FeatureStore

fs = FeatureStore()

# List all available features
fs.list_features()

# Get specific features for a city
fs.get_features("Harrisburg PA", [
    "avg_temp_f",
    "safety_index",
    "education_score",
    "liveability_score"
])

# See city leaderboard
fs.get_leaderboard()
```

---

## Roadmap

The following enhancements are planned:

- [ ] **Data Quality Checks** — automated null %, value range, and 
      schema validation on every pipeline run
- [ ] **Data Drift Detection** — weekly comparison flagging features 
      that changed significantly from the prior run
- [ ] **FastAPI Endpoint** — expose the feature store over HTTP so 
      any service can query features via REST
- [ ] **Streamlit Dashboard** — interactive web app to visually 
      explore city scores and feature comparisons
- [ ] **Docker Container** — containerize the full pipeline so anyone 
      can run it with a single command
- [ ] **CI/CD GitHub Action** — automatically run data quality checks 
      on every push to main
- [ ] **Additional Cities** — expand beyond 5 cities to full US coverage
- [ ] **Additional Data Sources** — air quality, cost of living, 
      walkability scores

---

## Tech Stack

`Python` · `Pandas` · `SQLite` · `SQL` · `REST APIs` · `Jupyter` · 
`Matplotlib` · `python-dotenv`

---

## Author

Built as a portfolio project for data engineering roles.

Save it with Ctrl + S, then push it to GitHub:
cmdgit add README.md
git commit -m "add full project README with roadmap"
git push
Let me know when it's pushed and we'll update the Jupyter notebook!You said: Can you put it all in so its copyableCan you put it all in so its copyable6:57 PMClaude responded: Here is the complete README.Here is the complete README.md — select all and copy:
markdown# LocalPulse 🏙️
### A Neighborhood Feature Store built with Python and SQL

A production-style data engineering project that ingests live weather, crime, and school quality data across US cities, engineers ML-ready features using SQL, and serves them through a versioned Python interface.

---

## What It Does

LocalPulse simulates the kind of infrastructure real ML teams depend on — a reliable, versioned source of clean features that any downstream model or analyst can query without re-engineering the pipeline themselves.

Every time the pipeline runs it:
1. Pulls live data from 3 public sources via REST APIs
2. Cleans and transforms raw data into engineered features using SQL
3. Joins all sources into a master feature table
4. Scores each city on liveability using a composite SQL model
5. Stores everything in a versioned feature registry

---

## Architecture
[Public APIs / Data Sources]
↓
[Ingestion Layer]          — feature_store/ingest.py
[                ]          — feature_store/ingest_crime.py
[                ]          — feature_store/ingest_schools.py
↓
[Transformation Layer]     — transforms/transform.py
↓
[Feature Store / Registry] — feature_store/feature_store.py
↓
[Demo Notebook]            — notebooks/demo.ipynb

---

## Data Sources

| Source | Data | Cost |
|---|---|---|
| Open-Meteo API | Live 7-day weather forecast | Free, no key needed |
| FBI UCR 2022 | State level violent and property crime rates | Free |
| Urban Institute Education Data Portal | School count, enrollment, student/teacher ratio | Free, no key needed |

---

## Feature Registry (13 Features)

| Feature | Description | Source |
|---|---|---|
| `avg_temp_f` | Average temperature in Fahrenheit | Weather |
| `temp_range_f` | Difference between max and min temp | Weather |
| `temp_category` | Hot / warm / mild / cold label | Weather |
| `precipitation_category` | Wet / moderate / dry label | Weather |
| `temp_stability` | High / moderate / stable variability | Weather |
| `violent_crime_rate` | Violent crimes per 100k people | Crime |
| `property_crime_rate` | Property crimes per 100k people | Crime |
| `safety_index` | Safety score 0-100 | Crime |
| `safety_category` | Safe / moderate / high crime label | Crime |
| `student_teacher_ratio` | Students per teacher | Schools |
| `education_score` | Education quality score 0-100 | Schools |
| `education_category` | Excellent / good / average / poor label | Schools |
| `liveability_score` | Composite city liveability score 0-100 | All sources |

---

## Project Structure
localpulse/
│
├── raw/                        ← downloaded data CSVs
├── transforms/
│   └── transform.py            ← SQL feature engineering
├── feature_store/
│   ├── feature_store.py        ← FeatureStore Python class
│   ├── ingest.py               ← weather ingestion
│   ├── ingest_crime.py         ← crime data ingestion
│   └── ingest_schools.py       ← school data ingestion
├── notebooks/
│   └── demo.ipynb              ← Jupyter demo notebook
├── .env                        ← API keys (never committed)
├── .gitignore
├── requirements.txt
└── README.md

---

## How To Run

### 1. Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/localpulse.git
cd localpulse
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API key
Create a `.env` file in the root folder:
API_DATA_GOV_KEY=your_key_here

### 4. Run the full pipeline
```bash
# Ingest all data sources
python feature_store/ingest.py
python feature_store/ingest_crime.py
python feature_store/ingest_schools.py

# Transform and build feature tables
python transforms/transform.py

# Register all features
python feature_store/feature_store.py
```

### 5. Open the demo notebook
```bash
jupyter notebook
```
Navigate to `notebooks/demo.ipynb` and run all cells.

---

## Querying the Feature Store

```python
from feature_store.feature_store import FeatureStore

fs = FeatureStore()

# List all available features
fs.list_features()

# Get specific features for a city
fs.get_features("Harrisburg PA", [
    "avg_temp_f",
    "safety_index",
    "education_score",
    "liveability_score"
])

# See city leaderboard
fs.get_leaderboard()
```

---

## Roadmap

The following enhancements are planned:

- [ ] **Data Quality Checks** — automated null %, value range, and schema validation on every pipeline run
- [ ] **Data Drift Detection** — weekly comparison flagging features that changed significantly from the prior run
- [ ] **FastAPI Endpoint** — expose the feature store over HTTP so any service can query features via REST
- [ ] **Streamlit Dashboard** — interactive web app to visually explore city scores and feature comparisons
- [ ] **Docker Container** — containerize the full pipeline so anyone can run it with a single command
- [ ] **CI/CD GitHub Action** — automatically run data quality checks on every push to main
- [ ] **Additional Cities** — expand beyond 5 cities to full US coverage
- [ ] **Additional Data Sources** — air quality, cost of living, walkability scores

---

## Tech Stack

`Python` · `Pandas` · `SQLite` · `SQL` · `REST APIs` · `Jupyter` · `Matplotlib` · `python-dotenv`

---

