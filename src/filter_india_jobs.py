from pathlib import Path
import re

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = PROJECT_ROOT / "data" / "cleaned" / "cleaned_jobs.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned" / "india_jobs.csv"

INDIA_COUNTRY_PATTERN = re.compile(r"(?:^|,\s*)india(?:\s*,|$)", re.IGNORECASE)
INDIA_CITY_PATTERN = re.compile(
    r"\b(?:ahmedabad|bengaluru|bangalore|chandigarh|chennai|coimbatore|faridabad|"
    r"ghaziabad|gurgaon|gurugram|hyderabad|indore|jaipur|kanpur|kochi|kolkata|"
    r"lucknow|mumbai|nagpur|noida|patna|pune|surat|thane|vadodara|visakhapatnam)\b",
    re.IGNORECASE,
)


def is_india_location(value: object) -> bool:
    location = str(value).strip()
    return bool(INDIA_COUNTRY_PATTERN.search(location) or INDIA_CITY_PATTERN.search(location))


jobs = pd.read_csv(INPUT_PATH)
india_mask = jobs["location"].map(is_india_location)
india_jobs = jobs.loc[india_mask].copy()
india_jobs.to_csv(OUTPUT_PATH, index=False)

print(f"India jobs: {len(india_jobs)} rows")
print(f"Saved to: {OUTPUT_PATH}")

if india_jobs.empty:
    print("No reliable India postings were found in the current dataset.")