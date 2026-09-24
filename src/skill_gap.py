import sys
from pathlib import Path

# Add project root to sys.path so imports work universally
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Optional, Set
import json
import pandas as pd

try:
    from src.skills_taxonomy import normalize_skill
    from src.skill_demand import get_analyzer
    from src.market_saturation import get_saturation_level
except ModuleNotFoundError:
    from skills_taxonomy import normalize_skill
    from skill_demand import get_analyzer
    from market_saturation import get_saturation_level


class SkillGapAnalyzer:
    """
    Evaluates a user's current skillset against empirical market requirements
    for a chosen target canonical role.
    """

    def __init__(self):
        self.demand_analyzer = get_analyzer()

    def analyze_gap(
        self,
        user_skills: List[str],
        target_role: str,
        top_role_skills: int = 10,
    ) -> Dict:
        """
        Calculates skill match percentage, acquired skills, and prioritized missing skills.
        """
        # 1. Normalize user skills using taxonomy
        normalized_user_skills: Set[str] = set()
        for raw_s in user_skills:
            norm = normalize_skill(raw_s)
            if norm:
                normalized_user_skills.add(norm)
            elif raw_s.strip():
                normalized_user_skills.add(raw_s.strip().title())

        # 2. Fetch empirical requirements for target role
        role_demand_df = self.demand_analyzer.get_role_demand(target_role, top_n=top_role_skills)

        if role_demand_df.empty:
            return {
                "target_role": target_role,
                "status": "error",
                "message": f"Target role '{target_role}' has no postings in the dataset.",
                "match_percentage": 0.0,
                "acquired_skills": sorted(list(normalized_user_skills)),
                "missing_skills": []
            }

        # 3. Categorize acquired vs. missing skills
        required_skills_list = role_demand_df["skill"].tolist()
        acquired = []
        missing = []

        for _, row in role_demand_df.iterrows():
            skill = row["skill"]
            category = row["category"]
            demand_pct = float(row["role_demand_pct"])
            postings = int(row["postings_count"])

            # Determine Priority based on employer demand frequency
            if demand_pct >= 40.0:
                priority = "High"
            elif demand_pct >= 20.0:
                priority = "Medium"
            else:
                priority = "Low"

            # Check if user already possesses the skill
            if skill in normalized_user_skills:
                acquired.append({
                    "skill": skill,
                    "category": category,
                    "role_demand_pct": demand_pct
                })
            else:
                sat_info = get_saturation_level(skill)
                project_guidance = (
                    f"Build a portfolio project demonstrating practical use of '{skill}' "
                    f"in a real-world {target_role} workflow."
                )

                missing.append({
                    "skill": skill,
                    "category": category,
                    "role_demand_pct": demand_pct,
                    "postings_count": postings,
                    "priority": priority,
                    "saturation_level": sat_info.get("level", "Medium"),
                    "saturation_recommendation": sat_info.get("recommendation", ""),
                    "project_guidance": project_guidance
                })

        # 4. Calculate Role Match Percentage
        total_required = len(required_skills_list)
        match_pct = round((len(acquired) / total_required) * 100, 1) if total_required > 0 else 0.0

        return {
            "target_role": target_role,
            "status": "success",
            "total_benchmark_skills": total_required,
            "match_percentage": match_pct,
            "readiness_verdict": self._get_readiness_verdict(match_pct),
            "acquired_skills": acquired,
            "missing_skills": missing
        }

    def _get_readiness_verdict(self, match_pct: float) -> str:
        if match_pct >= 75.0:
            return "Job Ready - Strong competitive match for this role!"
        elif match_pct >= 40.0:
            return "Moderate Match - Close to role requirements with a few critical gaps."
        else:
            return "Early Stage - Significant skill gaps need to be addressed."


_gap_analyzer = None

def get_gap_analyzer() -> SkillGapAnalyzer:
    global _gap_analyzer
    if _gap_analyzer is None:
        _gap_analyzer = SkillGapAnalyzer()
    return _gap_analyzer


def get_skill_gap(user_skills: List[str], target_role: str) -> Dict:
    return get_gap_analyzer().analyze_gap(user_skills, target_role)


if __name__ == "__main__":
    analyzer = get_gap_analyzer()
    print("==================================================")
    print("           SKILL GAP ANALYSIS ENGINE TEST         ")
    print("==================================================\n")

    print("--- TEST CASE 1: Student targeting 'Data Scientist' ---")
    user_input = ["python", "sql", "git"]
    result = analyzer.analyze_gap(user_input, "Data Scientist")
    print(f"Target Role:      {result['target_role']}")
    print(f"Match Score:      {result['match_percentage']}% ({result['readiness_verdict']})")
    print(f"Acquired Skills:  {[s['skill'] for s in result['acquired_skills']]}")
    print(f"\nTop Missing Skills ({len(result['missing_skills'])}):")
    for m in result['missing_skills'][:5]:
        print(f"  * {m['skill']:<18} | Priority: {m['priority']:<6} | Demand: {m['role_demand_pct']:>4.1f}% | Saturation: {m['saturation_level']}")
    print()

    print("--- TEST CASE 2: Candidate with No Skills targeting 'Backend Developer' ---")
    result_empty = analyzer.analyze_gap([], "Backend Developer")
    print(f"Match Score:      {result_empty['match_percentage']}% ({result_empty['readiness_verdict']})")
    print(f"Missing Skills:   {len(result_empty['missing_skills'])} identified")
