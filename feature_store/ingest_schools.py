import requests
import pandas as pd
from datetime import datetime

# Education Data Portal - Urban Institute (completely free, no API key)
BASE_URL = "https://educationdata.urban.org/api/v1"

STATES = [
    {"name": "Pennsylvania",   "state_abbr": "PA", "fips": 42},
    {"name": "North Carolina", "state_abbr": "NC", "fips": 37},
    {"name": "New York",       "state_abbr": "NY", "fips": 36},
    {"name": "Texas",          "state_abbr": "TX", "fips": 48},
    {"name": "Illinois",       "state_abbr": "IL", "fips": 17},
]

def fetch_school_data(state):
    """Fetch school graduation rates and enrollment by state"""

    url = (
    f"{BASE_URL}/schools/ccd/directory/2021/"
    f"?fips={state['fips']}&fields=ncessch,school_name,enrollment,teachers_fte"
    f"&limit=2000"
)

    response = requests.get(url)

    if response.status_code != 200:
        raise ValueError(f"API error for {state['name']}: {response.status_code}")

    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"No results for {state['name']}")

    results = data["results"]
    df = pd.DataFrame(results)

    # Filter out bad data
    df = df[df["enrollment"]    > 0]
    df = df[df["teachers_fte"]  > 0]

    total_schools         = len(df)
    total_enrollment      = int(df["enrollment"].sum())
    avg_enrollment        = round(df["enrollment"].mean(), 1)
    total_teachers        = df["teachers_fte"].sum()
    student_teacher_ratio = round(total_enrollment / total_teachers, 1) if total_teachers > 0 else 0
    
    # Lower student/teacher ratio = better (more teachers per student)
    # National average is about 16:1
    ratio_score = round(max(0, 100 - (student_teacher_ratio / 16 * 50)), 1)

    return {
        "state":                  state["state_abbr"],
        "state_name":             state["name"],
        "total_schools":          total_schools,
        "total_enrollment":       int(total_enrollment),
        "avg_school_enrollment":  avg_enrollment,
        "student_teacher_ratio":  student_teacher_ratio,
        "education_score":        ratio_score,
        "education_category":     "excellent" if ratio_score >= 70 else
                                  "good"      if ratio_score >= 55 else
                                  "average"   if ratio_score >= 40 else
                                  "poor",
        "ingested_at":            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def run():
    print("Starting school data ingestion...\n")
    records = []
    errors  = []

    for state in STATES:
        print(f"  Fetching {state['name']}...")
        try:
            record = fetch_school_data(state)
            records.append(record)
            print(f"  Done — {record['total_schools']} schools, ratio: {record['student_teacher_ratio']}:1, score: {record['education_score']}")
        except ValueError as e:
            print(f"  ERROR: {e}")
            errors.append(state["name"])

    if records:
        df = pd.DataFrame(records)
        df.to_csv("raw/schools.csv", index=False)
        print(f"\nDone! Saved {len(df)} records to raw/schools.csv")
        print(df.to_string(index=False))

    if errors:
        print(f"\nFailed states: {errors}")


if __name__ == "__main__":
    run()