import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_ROOT / "data" / "skills" / "skills_taxonomy.json"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "processed" / "jobs_cleaned.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "job_skills.csv"


class SkillExtractor:
    """
    NLP Skill Extraction engine utilizing rule-based pattern matching
    grounded in our curated skills taxonomy.
    """

    def __init__(self, taxonomy_path: Path = TAXONOMY_PATH):
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.patterns = self._compile_patterns()

    def _load_taxonomy(self, path: Path) -> Dict[str, Dict[str, List[str]]]:
        if not path.exists():
            from src.skills_taxonomy import TAXONOMY_DATA
            return TAXONOMY_DATA
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _compile_patterns(self) -> List[Tuple[re.Pattern, str, str]]:
        compiled = []
        all_entries = []

        for category, skills in self.taxonomy.items():
            for canonical, aliases in skills.items():
                all_entries.append((canonical, canonical, category))
                for alias in aliases:
                    if alias.lower() != canonical.lower():
                        all_entries.append((alias, canonical, category))

        # Longest alias first to avoid substring collisions
        all_entries.sort(key=lambda x: len(x[0]), reverse=True)

        for phrase, canonical, category in all_entries:
            escaped = re.escape(phrase.lower())
            pattern_str = rf"(?<![a-zA-Z0-9_]){escaped}(?![a-zA-Z0-9_])"
            pattern = re.compile(pattern_str, re.IGNORECASE)
            compiled.append((pattern, canonical, category))

        return compiled

    def extract_skills(self, text: str) -> List[str]:
        if not text or not isinstance(text, str):
            return []
        matched_skills: Set[str] = set()
        text_lower = text.lower()
        for pattern, canonical, _ in self.patterns:
            if pattern.search(text_lower):
                matched_skills.add(canonical)
        return sorted(list(matched_skills))

    def extract_skills_with_categories(self, text: str) -> List[Dict[str, str]]:
        if not text or not isinstance(text, str):
            return []
        matched = {}
        text_lower = text.lower()
        for pattern, canonical, category in self.patterns:
            if canonical not in matched and pattern.search(text_lower):
                matched[canonical] = category
        return [
            {"skill": skill, "category": cat}
            for skill, cat in sorted(matched.items())
        ]


_extractor = None

def get_extractor() -> SkillExtractor:
    global _extractor
    if _extractor is None:
        _extractor = SkillExtractor()
    return _extractor


def extract_skills(text: str) -> List[str]:
    return get_extractor().extract_skills(text)


def process_dataset_skills(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
) -> pd.DataFrame:
    """
    Extracts skills for all jobs in the dataset and outputs the master
    job-to-skills relational table.
    """
    print(f"Loading cleaned dataset from: {input_path}")
    df = pd.read_csv(input_path)
    extractor = get_extractor()

    print(f"Extracting skills for {len(df):,} job postings...")
    records = []

    for _, row in df.iterrows():
        job_id = row.get("job_id")
        canonical_role = row.get("canonical_role", "Other / Domain Specialist")

        # Combine title, description, and tagged key_skills for comprehensive context
        combined_text = f"{row.get('title', '')} {row.get('description', '')} {row.get('key_skills', '')}"
        extracted = extractor.extract_skills_with_categories(combined_text)

        for item in extracted:
            records.append({
                "job_id": job_id,
                "canonical_role": canonical_role,
                "skill": item["skill"],
                "category": item["category"]
            })

    skills_df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    skills_df.to_csv(output_path, index=False)

    print("\n=== SKILL EXTRACTION COMPLETED ===")
    print(f"Total Skill Mentions Extracted: {len(skills_df):,}")
    print(f"Unique Jobs with Skills:        {skills_df['job_id'].nunique():,}")
    print(f"Unique Canonical Skills Found:  {skills_df['skill'].nunique():,}")
    print(f"Average Skills per Posting:     {len(skills_df) / len(df):.1f}")
    print(f"Saved to: {output_path}")

    return skills_df


if __name__ == "__main__":
    process_dataset_skills()
