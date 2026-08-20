import pandas as pd

jobs = pd.read_csv("data/cleaned/cleaned_jobs.csv")
skills = pd.read_csv("data/skill_list.csv")["skill"].dropna().str.lower().str.strip().tolist()

results = []
for i, row in jobs.iterrows():
    text = str(row["description"]).lower()
    for s in skills:
        if s in text:
            results.append({"job_id": row.get("job_id", i), "skill": s})

pd.DataFrame(results).to_csv("data/cleaned/job_skills.csv", index=False)
print(f"Done — extracted {len(results)} skill mentions")