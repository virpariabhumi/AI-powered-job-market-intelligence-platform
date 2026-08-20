import pandas as pd

df = pd.read_csv("data/cleaned/trimmed_jobs.csv")

df = df.drop_duplicates()
df = df.dropna(subset=["title", "description"])
df["title"] = df["title"].str.lower().str.strip()

df.to_csv("data/cleaned/cleaned_jobs.csv", index=False)
print(f"Cleaned dataset: {len(df)} rows")