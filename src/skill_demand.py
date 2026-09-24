from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOB_SKILLS_PATH = PROJECT_ROOT / "data" / "processed" / "job_skills.csv"
JOBS_PATH = PROJECT_ROOT / "data" / "processed" / "jobs_cleaned.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "skills"


class SkillDemandAnalyzer:
    """
    Computes statistical labor-market demand metrics for skills across
    the entire dataset and conditioned on specific canonical roles.
    """

    def __init__(
        self,
        job_skills_path: Path = JOB_SKILLS_PATH,
        jobs_path: Path = JOBS_PATH,
    ):
        self.job_skills = pd.read_csv(job_skills_path)
        self.total_jobs = len(pd.read_csv(jobs_path))
        self.jobs_with_skills = self.job_skills["job_id"].nunique()

    def get_overall_demand(self, top_n: int = 25) -> pd.DataFrame:
        """
        Calculates top skills across the entire job market with frequencies
        and market penetration percentages.
        """
        counts = self.job_skills["skill"].value_counts().head(top_n).reset_index()
        counts.columns = ["skill", "postings_count"]
        counts["market_share_pct"] = (
            (counts["postings_count"] / self.total_jobs) * 100
        ).round(2)
        return counts

    def get_category_demand(self) -> pd.DataFrame:
        """
        Aggregates skill demand across the 7 taxonomy categories.
        """
        cat_counts = self.job_skills["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "total_mentions"]
        cat_counts["share_pct"] = (
            (cat_counts["total_mentions"] / len(self.job_skills)) * 100
        ).round(2)
        return cat_counts

    def get_role_demand(
        self, canonical_role: str, top_n: int = 15
    ) -> pd.DataFrame:
        """
        Calculates skill demand conditioned on a specific canonical role.
        """
        role_subset = self.job_skills[
            self.job_skills["canonical_role"].str.lower() == canonical_role.lower()
        ]

        if role_subset.empty:
            return pd.DataFrame(columns=["skill", "category", "postings_count", "role_demand_pct"])

        role_job_count = role_subset["job_id"].nunique()
        counts = (
            role_subset.groupby(["skill", "category"])
            .size()
            .reset_index(name="postings_count")
            .sort_values(by="postings_count", ascending=False)
            .head(top_n)
        )
        counts["role_demand_pct"] = (
            (counts["postings_count"] / role_job_count) * 100
        ).round(2)
        return counts

    def export_analytics_for_frontend(self, output_dir: Path = OUTPUT_DIR) -> None:
        """
        Exports clean JSON analytics files for Member 2 to render dashboard charts.
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Overall Top 25 Skills
        overall = self.get_overall_demand(25).to_dict(orient="records")
        with open(output_dir / "overall_skill_demand.json", "w", encoding="utf-8") as f:
            json.dump(overall, f, indent=2)

        # 2. Category Breakdown
        categories = self.get_category_demand().to_dict(orient="records")
        with open(output_dir / "category_demand.json", "w", encoding="utf-8") as f:
            json.dump(categories, f, indent=2)

        # 3. Role-by-Role Top Skills for all major roles
        roles = [
            r for r in self.job_skills["canonical_role"].unique()
            if r != "Other / Domain Specialist"
        ]
        role_breakdown = {}
        for role in roles:
            role_breakdown[role] = self.get_role_demand(role, 12).to_dict(orient="records")

        with open(output_dir / "role_skill_demand.json", "w", encoding="utf-8") as f:
            json.dump(role_breakdown, f, indent=2)

        print(f"Exported frontend analytics JSONs to: {output_dir}")


_analyzer = None

def get_analyzer() -> SkillDemandAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = SkillDemandAnalyzer()
    return _analyzer


def get_role_skills(role: str, top_n: int = 10) -> List[str]:
    """
    Public helper to quickly fetch top skill names for a role.
    """
    df = get_analyzer().get_role_demand(role, top_n)
    return df["skill"].tolist() if not df.empty else []


if __name__ == "__main__":
    analyzer = get_analyzer()
    print("==================================================")
    print("          LABOR MARKET SKILL DEMAND REPORT        ")
    print("==================================================\n")

    print("1. TOP 10 SKILLS IN OVERALL MARKET:")
    print(analyzer.get_overall_demand(10).to_string(index=False))
    print()

    print("2. DEMAND BY CATEGORY DOMAIN:")
    print(analyzer.get_category_demand().to_string(index=False))
    print()

    print("3. TOP SKILLS FOR 'Data Scientist':")
    print(analyzer.get_role_demand("Data Scientist", 8).to_string(index=False))
    print()

    print("4. TOP SKILLS FOR 'Backend Developer':")
    print(analyzer.get_role_demand("Backend Developer", 8).to_string(index=False))
    print()

    analyzer.export_analytics_for_frontend()
