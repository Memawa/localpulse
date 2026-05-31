import requests
import pandas as pd

url = (
    "https://educationdata.urban.org/api/v1/schools/ccd/directory/2021/"
    "?fips=42&fields=ncessch,school_name,enrollment,teachers_fte&limit=10"
)

response = requests.get(url)
data = response.json()

df = pd.DataFrame(data["results"])
print("Columns returned:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())