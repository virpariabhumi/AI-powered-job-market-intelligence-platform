import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.role_standardization import standardize_role
from src.skills_taxonomy import normalize_skill, TAXONOMY_DATA
from src.skill_extraction import extract_skills
from src.skill_demand import get_analyzer
from src.skill_graph import get_graph, get_companion_skills
from src.market_saturation import get_saturation_level
from src.skill_gap import get_skill_gap


def run_tests():
    print("==================================================")
    print("   AI-POWERED JOB INTELLIGENCE: PIPELINE TESTS    ")
    print("==================================================\n")
    passed = 0
    total = 7

    # 1. Test Role Standardization
    try:
        assert standardize_role("Senior Data Scientist") == "Data Scientist"
        assert standardize_role("Full Stack Web Developer") == "Full Stack Developer"
        print("[PASS] Test 1: Role Standardization maps raw titles to canonical roles.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 1: Role Standardization failed: {e}")

    # 2. Test Skills Taxonomy
    try:
        assert normalize_skill("core java") == "Java"
        assert normalize_skill("data analytics") == "Data Analysis"
        assert normalize_skill("k8s") == "Kubernetes"
        print("[PASS] Test 2: Skills Taxonomy normalizes aliases accurately.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 2: Skills Taxonomy failed: {e}")

    # 3. Test NLP Skill Extraction
    try:
        text = "Seeking Python dev with C++, C#, .NET, Docker, and React.js experience."
        extracted = extract_skills(text)
        assert "Python" in extracted
        assert "C++" in extracted
        assert "C#" in extracted
        assert "Docker" in extracted
        assert "React" in extracted
        print(f"[PASS] Test 3: NLP Skill Extraction captured symbolic and aliased skills: {extracted}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 3: NLP Skill Extraction failed: {e}")

    # 4. Test Skill Demand Analysis
    try:
        analyzer = get_analyzer()
        demand = analyzer.get_overall_demand(5)
        assert len(demand) == 5
        assert "postings_count" in demand.columns
        print("[PASS] Test 4: Skill Demand Analysis computed market-wide frequencies.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 4: Skill Demand Analysis failed: {e}")

    # 5. Test Demand-Weighted Skill Graph (Unique Feature #2)
    try:
        companions = get_companion_skills("Python", top_n=3)
        assert len(companions) > 0
        assert "co_occurrence" in companions[0]
        print(f"[PASS] Test 5: Skill Graph queried companions for 'Python': {[c['skill'] for c in companions]}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 5: Skill Graph failed: {e}")

    # 6. Test Market Saturation Warning (Unique Feature #3)
    try:
        sat_sql = get_saturation_level("SQL")
        sat_docker = get_saturation_level("Docker")
        assert sat_sql["level"] in ["High", "Medium", "Low"]
        assert "explanation" in sat_sql
        print(f"[PASS] Test 6: Market Saturation returned levels (SQL: {sat_sql['level']}, Docker: {sat_docker['level']}).")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 6: Market Saturation failed: {e}")

    # 7. Test Skill Gap Analysis (Feeds Unique Feature #1)
    try:
        gap = get_skill_gap(["python", "sql"], "Data Scientist")
        assert gap["status"] == "success"
        assert "match_percentage" in gap
        assert len(gap["missing_skills"]) > 0
        print(f"[PASS] Test 7: Skill Gap Analysis calculated match score: {gap['match_percentage']}% with {len(gap['missing_skills'])} missing gaps.")
        passed += 1
    except Exception as e:
        print(f"[FAIL] Test 7: Skill Gap Analysis failed: {e}")

    print("\n==================================================")
    print(f"       TEST RESULTS: {passed}/{total} SUITES PASSED       ")
    print("==================================================")

    if passed == total:
        print("ALL SYSTEMS OPERATIONAL! Intelligence layer is ready for Member 2 handoff.\n")
    else:
        print("WARNING: Some tests failed. Review outputs above.\n")


if __name__ == "__main__":
    run_tests()
