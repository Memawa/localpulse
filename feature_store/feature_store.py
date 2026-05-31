import sqlite3
import pandas as pd
from datetime import datetime

class FeatureStore:
    
    def __init__(self, db_path="feature_store/localpulse.db"):
        self.db_path = db_path
        self._init_registry()
        print(f"FeatureStore connected to {db_path}")

    def _init_registry(self):
        """Creates the feature registry table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feature_registry (
                feature_name    TEXT,
                version         INTEGER,
                description     TEXT,
                source_table    TEXT,
                created_at      TEXT,
                PRIMARY KEY (feature_name, version)
            )
        """)
        conn.commit()
        conn.close()

    def register_feature(self, feature_name, description, source_table, version=1):
        """Register a feature in the registry"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO feature_registry 
            (feature_name, version, description, source_table, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (feature_name, version, description, source_table, 
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
        print(f"Registered feature: {feature_name} (v{version})")

    def get_features(self, city, feature_list):
        """Query features for a specific city"""
        conn = sqlite3.connect(self.db_path)
        columns = ", ".join(["city"] + feature_list)
        query = f"""
            SELECT {columns}
            FROM weather_features
            WHERE city = ?
        """
        df = pd.read_sql_query(query, conn, params=(city,))
        conn.close()
        
        if df.empty:
            print(f"No data found for city: {city}")
        return df

    def list_features(self):
        """Show all registered features"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM feature_registry", conn)
        conn.close()
        
        if df.empty:
            print("No features registered yet.")
        else:
            print("\nRegistered Features:")
            print(df.to_string(index=False))
        return df

    def get_all_cities(self):
        """List all available cities in the store"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT city FROM weather_features", conn)
        conn.close()
        print("\nAvailable cities:", df["city"].tolist())
        return df["city"].tolist()


if __name__ == "__main__":
   if __name__ == "__main__":
    fs = FeatureStore()

    # Clear old registry and re-register everything fresh
    conn = sqlite3.connect(fs.db_path)
    conn.execute("DELETE FROM feature_registry")
    conn.commit()
    conn.close()
    print("Registry cleared\n")

    # Weather features
    fs.register_feature("avg_temp_f",              "Average temp in Fahrenheit",               "weather_features")
    fs.register_feature("temp_range_f",            "Difference between max and min temp in F",  "weather_features")
    fs.register_feature("precipitation_category",  "Wet / moderate / dry classification",       "weather_features")
    fs.register_feature("temp_category",           "Hot / warm / mild / cold label",            "weather_features")
    fs.register_feature("temp_stability",          "High / moderate / stable temp variability", "weather_features")

    # Crime features
    fs.register_feature("violent_crime_rate",      "Violent crimes per 100k people",            "crime_features")
    fs.register_feature("property_crime_rate",     "Property crimes per 100k people",           "crime_features")
    fs.register_feature("safety_index",            "Safety score 0-100 (higher = safer)",       "crime_features")
    fs.register_feature("safety_category",         "Safe / moderate / high crime label",        "crime_features")

    # School features
    fs.register_feature("student_teacher_ratio",   "Students per teacher",                      "school_features")
    fs.register_feature("education_score",         "Education quality score 0-100",             "school_features")
    fs.register_feature("education_category",      "Excellent / good / average / poor label",   "school_features")

    # List all registered features
    fs.list_features()

    # See available cities
    fs.get_all_cities()

    # Test query from master table
    conn = sqlite3.connect(fs.db_path)
    print("\nMaster features for Harrisburg PA:")
    df = pd.read_sql_query("SELECT * FROM master_features WHERE city = 'Harrisburg PA'", conn)
    print(df.to_string(index=False))
    conn.close()