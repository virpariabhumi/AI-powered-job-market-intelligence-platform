from pathlib import Path
from typing import Dict, List, Optional
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JOB_SKILLS_PATH = PROJECT_ROOT / "data" / "processed" / "job_skills.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "skills" / "market_saturation.json"


class MarketSaturationAnalyzer:
    """
    Computes explainable market saturation proxies for skills based on:
      1. Demand Prevalence: Overall market frequency
      2. Role Breadth: Cross-role ubiquity across canonical job roles
    """

    def __init__(self, job_skills_path: Path = JOB_SKILLS_PATH):
        self.df = pd.read_csv(job_skills_path)
        self.total_jobs = self.df["job_id"].nunique()
        self.total_roles = self.df["canonical_role"].nunique()
        self.saturation_cache = self._compute_all_saturations()

    def _compute_all_saturations(self) -> Dict[str, Dict]:
        """
        Pre-computes saturation metrics for all canonical skills.
        """
        cache = {}
        skill_groups = self.df.groupby("skill")
        max_skill_count = self.df["skill"].value_counts().max()

        for skill, group in skill_groups:
            postings_count = len(group)
            roles_covered = group["canonical_role"].nunique()
            category = group["category"].iloc[0]

            # 1. Frequency factor normalized (0.0 to 1.0)
            freq_score = postings_count / max_skill_count

            # 2. Role breadth factor (0.0 to 1.0)
            breadth_score = roles_covered / self.total_roles

            # Composite Saturation Index (0 to 100)
            raw_score = (0.60 * freq_score + 0.40 * breadth_score) * 100
            score = round(raw_score, 1)

            # Classify into Low / Medium / High
            if score >= 65:
                level = "High"
                explanation = (
                    f"'{skill}' appears ubiquitously across {roles_covered} different roles. "
                    f"Because a vast majority of candidates know this skill, it has high market saturation."
                )
                recommendation = (
                    f"Do not rely solely on '{skill}'. Pair it with complementary specialized "
                    f"skills from your skill graph to stand out."
                )
            elif score >= 35:
                level = "Medium"
                explanation = (
                    f"'{skill}' has healthy, steady demand across {roles_covered} roles "
                    f"with moderate candidate supply."
                )
                recommendation = (
                    f"Valuable core skill. Build practical end-to-end projects demonstrating '{skill}' "
                    f"to prove competency."
                )
            else:
                level = "Low"
                explanation = (
                    f"'{skill}' is a specialized or emerging technology with lower candidate saturation "
                    f"and focused role demand."
                )
                recommendation = (
                    f"Excellent differentiator! Mastering '{skill}' can significantly boost your "
                    f"profile visibility for specialized positions."
                )

            cache[skill] = {
                "skill": skill,
                "category": category,
                "postings_count": int(postings_count),
                "roles_covered": int(roles_covered),
                "saturation_score": score,
                "level": level,
                "explanation": explanation,
                "recommendation": recommendation
            }

        return cache

    def get_saturation(self, skill: str) -> Optional[Dict]:
        """
        Public query function to retrieve the saturation profile for any skill.
        """
        skill_clean = skill.strip().lower()
        for k, v in self.saturation_cache.items():
            if k.lower() == skill_clean:
                return v
        return None

    def export_saturation_report(self, output_path: Path = OUTPUT_PATH) -> None:
        """
        Exports the entire saturation knowledge base to JSON for Member 2's frontend.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.saturation_cache, f, indent=2)
        print(f"Market Saturation report exported to: {output_path}")


_saturation_analyzer = None

def get_saturation_analyzer() -> MarketSaturationAnalyzer:
    global _saturation_analyzer
    if _saturation_analyzer is None:
        _saturation_analyzer = MarketSaturationAnalyzer()
    return _saturation_analyzer


def get_saturation_level(skill: str) -> Dict:
    """
    Public API helper function for Member 2's FastAPI integration.
    """
    res = get_saturation_analyzer().get_saturation(skill)
    if res:
        return res
    return {
        "skill": skill,
        "level": "Unknown",
        "saturation_score": 0.0,
        "explanation": f"Skill '{skill}' was not found in the current labor market dataset.",
        "recommendation": "Consult the general technology roadmap."
    }


if __name__ == "__main__":
    analyzer = get_saturation_analyzer()
    print("==================================================")
    print("         MARKET SATURATION WARNING ENGINE         ")
    print("==================================================\n")

    test_skills = ["SQL", "Python", "Docker", "PyTorch", "Kubernetes", "Excel"]
    for s in test_skills:
        info = analyzer.get_saturation(s)
        if info:
            print(f"Skill: {info['skill']:<15} | Level: {info['level']:<6} | Score: {info['saturation_score']:>4.1f}/100")
            print(f"  Explanation:    {info['explanation']}")
            print(f"  Recommendation: {info['recommendation']}\n")

    analyzer.export_saturation_report()
