import pandas as pd

df = pd.read_csv("data/raw/raw_jobs.csv")
print(df.shape)
print(df.columns.tolist())

keep_cols = [
    "job_id", "title", "description",
    "formatted_experience_level", "formatted_work_type",
    "location", "original_listed_time", "views", "applies", "remote_allowed"
]
keep_cols = [c for c in keep_cols if c in df.columns]

df = df[keep_cols]
df.to_csv("data/cleaned/trimmed_jobs.csv", index=False)
print(f"Kept {len(keep_cols)} columns, {len(df)} rows")