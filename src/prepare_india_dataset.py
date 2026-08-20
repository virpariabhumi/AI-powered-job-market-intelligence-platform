from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "data" / "cleaned" / "india_jobs_cleaned.csv"


def load_split(path: Path, split_name: str) -> pd.DataFrame:
    data = pd.read_csv(path)
    data = data.rename(
        columns={
            "job_desig": "title",
            "job_description": "description",
            "experience": "formatted_experience_level",
            "job_type": "formatted_work_type",
        }
    )
    source_ids = data["Unnamed: 0"] if "Unnamed: 0" in data else pd.Series(data.index, index=data.index)
    data["job_id"] = split_name + "-" + source_ids.astype(str)
    data["source_split"] = split_name
    for column in ["salary", "key_skills", "company_name_encoded"]:
        if column not in data:
            data[column] = pd.NA
    return data[
        [
            "job_id",
            "title",
            "description",
            "formatted_experience_level",
            "formatted_work_type",
            "location",
            "salary",
            "key_skills",
            "company_name_encoded",
            "source_split",
        ]
    ]


train = load_split(RAW_DIR / "india_jobs_train.csv", "train")
test = load_split(RAW_DIR / "india_jobs_test.csv", "test")
jobs = pd.concat([train, test], ignore_index=True)
jobs = jobs.drop_duplicates(subset=["title", "description", "location"])
jobs = jobs.dropna(subset=["title", "description", "location"])
jobs["title"] = jobs["title"].astype(str).str.lower().str.strip()
jobs["location"] = jobs["location"].astype(str).str.strip()
jobs.to_csv(OUTPUT_PATH, index=False)

print(f"India jobs prepared: {len(jobs)} rows")
print(f"Saved to: {OUTPUT_PATH}")
print(f"Locations: {jobs['location'].nunique()} unique")