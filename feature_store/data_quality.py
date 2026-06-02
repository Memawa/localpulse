import sqlite3
import pandas as pd

# Validation rules for each feature table.
# required_columns: must exist and must not be null
# ranges: (min, max) sanity bounds for numeric columns
QUALITY_RULES = {

    "weather_features": {
        "required_columns": [
            "city", "state", "avg_temp_f", "temp_range_f",
            "total_precipitation", "temp_category",
            "precipitation_category", "temp_stability"
        ],
        "ranges": {
            "avg_temp_f":          (-30, 130),  # Fahrenheit, US cities
            "temp_range_f":        (0, 100),     # max - min, can't be negative
            "total_precipitation": (0, 500),     # mm over 7 days
        }
    },

    "crime_features": {
        "required_columns": [
            "state", "violent_crime_rate", "property_crime_rate",
            "safety_index", "safety_category"
        ],
        "ranges": {
            "violent_crime_rate":  (0, 5000),   # per 100k people
            "property_crime_rate": (0, 10000),  # per 100k people
            "safety_index":        (0, 100),    # engineered score
        }
    },

    "school_features": {
        "required_columns": [
            "state", "student_teacher_ratio",
            "education_score", "education_category"
        ],
        "ranges": {
            "student_teacher_ratio": (1, 100),  # below 1 or above 100 = corrupted
            "education_score":       (0, 100),  # engineered score
        }
    },

    "liveability_features": {
        "required_columns": [
            "city", "state", "liveability_score"
        ],
        "ranges": {
            "liveability_score": (0, 100),  # bounded by SQL MIN(100, MAX(0,...))
        }
    },
}


def check_schema(df, table_name, required_columns):
    """Returns PASS/FAIL for whether all required columns exist in the table."""
    results = []
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        results.append({
            "check": "schema", "table": table_name,
            "column": ", ".join(missing), "status": "FAIL",
            "detail": f"Missing columns: {missing}"
        })
    else:
        results.append({
            "check": "schema", "table": table_name,
            "column": "all", "status": "PASS",
            "detail": f"All {len(required_columns)} required columns present"
        })

    return results


def check_nulls(df, table_name, required_columns):
    """Returns PASS/WARN/FAIL per column based on null percentage.
    WARN = 1-20% null, FAIL = >20% null or empty table.
    """
    results = []

    for col in required_columns:
        if col not in df.columns:
            # schema check already flagged this — skip to avoid duplicate noise
            continue

        null_count = df[col].isnull().sum()
        total_rows = len(df)

        if total_rows == 0:
            results.append({
                "check": "nulls", "table": table_name, "column": col,
                "status": "FAIL", "detail": "Table is empty — no rows found"
            })
            continue

        null_pct = round((null_count / total_rows) * 100, 1)

        if null_pct == 0:
            status, detail = "PASS", "No nulls"
        elif null_pct <= 20:
            status = "WARN"
            detail = f"{null_count}/{total_rows} rows null ({null_pct}%)"
        else:
            status = "FAIL"
            detail = f"{null_count}/{total_rows} rows null ({null_pct}%) — exceeds 20% threshold"

        results.append({
            "check": "nulls", "table": table_name,
            "column": col, "status": status, "detail": detail
        })

    return results


def check_ranges(df, table_name, ranges):
    """Returns PASS/FAIL per column based on whether values fall within allowed bounds."""
    results = []

    for col, (min_allowed, max_allowed) in ranges.items():
        if col not in df.columns:
            continue

        series = df[col].dropna()  # nulls handled separately

        if series.empty:
            continue

        actual_min = series.min()
        actual_max = series.max()

        if (actual_min < min_allowed) or (actual_max > max_allowed):
            results.append({
                "check": "range", "table": table_name, "column": col,
                "status": "FAIL",
                "detail": (
                    f"Values out of bounds [{min_allowed}, {max_allowed}]: "
                    f"actual range [{actual_min}, {actual_max}]"
                )
            })
        else:
            results.append({
                "check": "range", "table": table_name, "column": col,
                "status": "PASS",
                "detail": f"Range OK [{actual_min}, {actual_max}] within [{min_allowed}, {max_allowed}]"
            })

    return results


def run_quality_checks(db_path="feature_store/localpulse.db"):
    """Run schema, null, and range checks on all feature tables.
    Raises ValueError if any check fails — prevents bad data flowing downstream.
    """
    print("\n" + "=" * 60)
    print("  DATA QUALITY REPORT")
    print("=" * 60)

    conn = sqlite3.connect(db_path)
    all_results = []

    for table_name, rules in QUALITY_RULES.items():
        print(f"\n[ {table_name} ]")

        try:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        except Exception as e:
            all_results.append({
                "check": "schema", "table": table_name,
                "column": "—", "status": "FAIL",
                "detail": f"Could not load table: {e}"
            })
            print(f"  FAIL  Table not found or unreadable: {e}")
            continue

        results = []
        results += check_schema(df, table_name, rules["required_columns"])
        results += check_nulls(df, table_name, rules["required_columns"])
        results += check_ranges(df, table_name, rules.get("ranges", {}))

        for r in results:
            icon = {"PASS": "[OK]  ", "WARN": "[WARN]", "FAIL": "[FAIL]"}[r["status"]]
            print(f"  {icon}  {r['check']:<8} {r['column']:<28} {r['detail']}")

        all_results.extend(results)

    conn.close()

    total  = len(all_results)
    passed = sum(1 for r in all_results if r["status"] == "PASS")
    warned = sum(1 for r in all_results if r["status"] == "WARN")
    failed = sum(1 for r in all_results if r["status"] == "FAIL")

    print("\n" + "=" * 60)
    print(f"  SUMMARY: {total} checks — {passed} passed, {warned} warnings, {failed} failed")
    print("=" * 60 + "\n")

    if failed > 0:
        raise ValueError(
            f"Data quality check failed: {failed} critical issue(s) found. "
            "Review the report above before proceeding."
        )

    return all_results


if __name__ == "__main__":
    run_quality_checks()
