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
    fs = FeatureStore()

    # Register your features
    fs.register_feature("avg_temp",                "Average of max and min temp",        "weather_features")
    fs.register_feature("temp_range",              "Difference between max and min temp", "weather_features")
    fs.register_feature("precipitation_category",  "Wet / moderate / dry classification", "weather_features")
    fs.register_feature("temp_category",           "Hot / warm / mild / cold label",      "weather_features")

    # List all registered features
    fs.list_features()

    # See available cities
    fs.get_all_cities()

    # Query features for a specific city
    print("\nFeatures for Austin:")
    print(fs.get_features("Austin", ["avg_temp", "temp_range", "temp_category"]))