import json
import re
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_cleaned.csv"
ROLES_OUTPUT_PATH = PROJECT_ROOT / "data" / "canonical_roles.json"

# Rule hierarchy: ordered from most specific to general
ROLE_PATTERNS = [
    # Data & AI Family
    (r"\b(?:machine learning|ml engineer|deep learning|ai engineer|nlp engineer)\b", "Machine Learning Engineer"),
    (r"\b(?:data scientist|data science|applied scientist)\b", "Data Scientist"),
    (r"\b(?:data engineer|big data|etl developer|data pipeline)\b", "Data Engineer"),
    (r"\b(?:data analyst|bi analyst|business intelligence|analytics analyst|power bi developer|tableau developer)\b", "Data Analyst"),
    (r"\b(?:business analyst|ba\b|functional analyst|process analyst)\b", "Business Analyst"),

    # Software Engineering Family
    (r"\b(?:full stack|fullstack)\b", "Full Stack Developer"),
    (r"\b(?:frontend|front-end|front end|ui\/ux developer|react developer|angular developer|web developer)\b", "Frontend Developer"),
    (r"\b(?:backend|back-end|back end|java developer|python developer|node developer|golang|c\+\+ developer|\.net developer)\b", "Backend Developer"),
    (r"\b(?:android developer|ios developer|mobile app developer|flutter developer|react native)\b", "Mobile App Developer"),
    (r"\b(?:software engineer|software developer|swe\b|programmer|application developer)\b", "Software Engineer"),

    # DevOps, Cloud & QA
    (r"\b(?:devops|sre|site reliability|cloud engineer|aws engineer|azure engineer|infrastructure engineer)\b", "DevOps / Cloud Engineer"),
    (r"\b(?:quality analyst|qa analyst|qa engineer|software tester|automation tester|test engineer|quality assurance)\b", "QA / Test Engineer"),
    (r"\b(?:cyber ?security|infosec|information security|vulnerability|exploit|penetration tester|soc analyst)\b", "Cybersecurity Analyst"),

    # Product & Management
    (r"\b(?:product manager|product owner|associate product manager)\b", "Product Manager"),
    (r"\b(?:project manager|program manager|delivery manager|scrum master|pmp)\b", "Project Manager"),

    # Marketing & Digital
    (r"\b(?:digital marketing|seo|sem|social media manager|content marketing|growth marketing)\b", "Digital Marketing Specialist"),
]


def standardize_role(raw_title: object) -> str:
    """
    Standardizes raw, messy job titles into canonical industry roles.
    """
    if pd.isna(raw_title):
        return "Other / Domain Specialist"

    title_clean = str(raw_title).lower().strip()

    for pattern, canonical_role in ROLE_PATTERNS:
        if re.search(pattern, title_clean):
            return canonical_role

    return "Other / Domain Specialist"


def apply_role_standardization(
    dataset_path: Path = DATASET_PATH,
    roles_output_path: Path = ROLES_OUTPUT_PATH,
) -> pd.DataFrame:
    """
    Maps all titles in the dataset to canonical roles, updates the dataset,
    and exports a canonical roles list for Member 2's frontend dropdown.
    """
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)

    print("Mapping raw titles to canonical roles...")
    df["canonical_role"] = df["title"].apply(standardize_role)

    # Calculate role distribution
    role_counts = df["canonical_role"].value_counts()
    print("\n=== CANONICAL ROLE DISTRIBUTION ===")
    for role, count in role_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {role:<30} : {count:>5,} postings ({pct:>5.1f}%)")

    # Save updated dataset with canonical_role column
    df.to_csv(dataset_path, index=False)
    print(f"\nUpdated master dataset saved to: {dataset_path}")

    # Export frontend dropdown list for Member 2 (excluding 'Other')
    frontend_roles = [
        {"role": role, "postings_count": int(count)}
        for role, count in role_counts.items()
        if role != "Other / Domain Specialist"
    ]
    with open(roles_output_path, "w", encoding="utf-8") as f:
        json.dump(frontend_roles, f, indent=2)

    print(f"Exported {len(frontend_roles)} canonical roles for Member 2 to: {roles_output_path}")

    return df


if __name__ == "__main__":
    apply_role_standardization()
