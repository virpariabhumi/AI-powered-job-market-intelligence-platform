import argparse
import re
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract skills from job records.")
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "data" / "cleaned" / "cleaned_jobs.csv",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "data" / "cleaned" / "job_skills.csv",
    )
    return parser.parse_args()


args = parse_args()
jobs = pd.read_csv(args.input)
skills = pd.read_csv(PROJECT_ROOT / "data" / "skill_list.csv")["skill"].dropna().str.lower().str.strip().tolist()
skill_patterns = {
    skill: re.compile(r"(?<!\w)" + re.escape(skill) + r"(?!\w)")
    for skill in skills
}

results = []
for i, row in jobs.iterrows():
    text_parts = [str(row.get("title", "")), str(row.get("description", ""))]
    if "key_skills" in row.index:
        text_parts.append(str(row["key_skills"]))
    text = " ".join(text_parts).lower()
    for skill, pattern in skill_patterns.items():
        if pattern.search(text):
            results.append({"job_id": row.get("job_id", i), "skill": skill})

pd.DataFrame(results, columns=["job_id", "skill"]).to_csv(args.output, index=False)
print(f"Done — extracted {len(results)} skill mentions")