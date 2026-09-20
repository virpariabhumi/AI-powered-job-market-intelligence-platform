import json
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = PROJECT_ROOT / "data" / "skills" / "skills_taxonomy.json"

# Curated Taxonomy with 7 domains and verified alias mappings
TAXONOMY_DATA = {
    "Programming Languages": {
        "Python": ["python", "py"],
        "Java": ["java", "core java", "j2ee", "j2se"],
        "JavaScript": ["javascript", "js", "ecmascript"],
        "TypeScript": ["typescript", "ts"],
        "C++": ["c++", "cpp"],
        "C#": ["c#", "csharp", "c sharp"],
        "C": ["c language"],
        "R": ["r programming", "r language"],
        "Go": ["golang", "go language"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "Kotlin": ["kotlin"],
        "Swift": ["swift"],
        "Scala": ["scala"],
        "Rust": ["rust"]
    },
    "Web & Frameworks": {
        "React": ["react", "react.js", "reactjs"],
        "Angular": ["angular", "angular.js", "angularjs"],
        "Vue.js": ["vue", "vue.js", "vuejs"],
        "Node.js": ["node", "node.js", "nodejs"],
        "Django": ["django"],
        "Flask": ["flask"],
        "FastAPI": ["fastapi"],
        "Spring Boot": ["spring boot", "springboot", "spring framework"],
        "Express.js": ["express", "express.js", "expressjs"],
        "ASP.NET": ["asp.net", ".net", "dotnet", ".net core"],
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "Bootstrap": ["bootstrap"],
        "Tailwind CSS": ["tailwind", "tailwindcss"],
        "REST API": ["rest", "restful", "rest api", "web services", "apis"],
        "GraphQL": ["graphql"],
        "jQuery": ["jquery"]
    },
    "Databases & Storage": {
        "SQL": ["sql"],
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "MongoDB": ["mongodb", "mongo"],
        "Oracle": ["oracle", "oracle database"],
        "SQL Server": ["sql server", "ms sql", "mssql"],
        "Redis": ["redis"],
        "Elasticsearch": ["elasticsearch"],
        "Cassandra": ["cassandra"],
        "Firebase": ["firebase"],
        "NoSQL": ["nosql"],
        "Hive": ["hive"],
        "Snowflake": ["snowflake"]
    },
    "Data Science & AI": {
        "Data Analysis": ["data analysis", "data analytics", "analytics"],
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning", "dl"],
        "Natural Language Processing": ["nlp", "natural language processing"],
        "Computer Vision": ["computer vision", "cv"],
        "Data Science": ["data science"],
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "Scikit-Learn": ["scikit-learn", "sklearn"],
        "TensorFlow": ["tensorflow", "tf"],
        "PyTorch": ["pytorch"],
        "Keras": ["keras"],
        "Apache Spark": ["spark", "apache spark", "pyspark"],
        "Hadoop": ["hadoop", "apache hadoop", "big data"],
        "SAS": ["sas"],
        "Data Mining": ["data mining"],
        "Algorithms": ["algorithms", "data structures", "dsa"]
    },
    "Cloud & DevOps": {
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure", "microsoft azure"],
        "Google Cloud Platform": ["gcp", "google cloud", "google cloud platform"],
        "Docker": ["docker", "containerization"],
        "Kubernetes": ["kubernetes", "k8s"],
        "Git": ["git", "github", "gitlab", "version control"],
        "CI/CD": ["ci/cd", "continuous integration", "jenkins"],
        "Linux": ["linux", "unix", "ubuntu"],
        "Terraform": ["terraform"],
        "Ansible": ["ansible"]
    },
    "BI & Analytics Tools": {
        "Power BI": ["power bi", "powerbi"],
        "Tableau": ["tableau"],
        "Excel": ["excel", "advanced excel", "vba", "spreadsheets"],
        "Google Analytics": ["google analytics"],
        "SEO": ["seo", "search engine optimization"],
        "SEM": ["sem", "digital marketing"]
    },
    "Management & Soft Skills": {
        "Business Analysis": ["business analysis", "ba", "requirements gathering"],
        "Communication": ["communication", "communication skills", "verbal communication"],
        "Problem Solving": ["problem solving", "analytical skills", "troubleshooting"],
        "Project Management": ["project management", "pmp"],
        "Agile": ["agile", "scrum", "scrum master"],
        "Leadership": ["leadership", "team management", "team leadership"],
        "Product Management": ["product management"],
        "Financial Analysis": ["financial analysis", "budgeting", "finance", "accounting"]
    }
}


def build_alias_map(taxonomy: Dict[str, Dict[str, List[str]]]) -> Dict[str, str]:
    """
    Creates a flat lowercase alias-to-canonical lookup dictionary.
    Example: {'js': 'JavaScript', 'k8s': 'Kubernetes'}
    """
    alias_map = {}
    for category, skills in taxonomy.items():
        for canonical, aliases in skills.items():
            alias_map[canonical.lower()] = canonical
            for alias in aliases:
                alias_map[alias.lower().strip()] = canonical
    return alias_map


def export_taxonomy(output_path: Path = TAXONOMY_PATH) -> None:
    """
    Exports the structured taxonomy to JSON.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(TAXONOMY_DATA, f, indent=2)
    print(f"Taxonomy successfully exported to: {output_path}")


def load_taxonomy(input_path: Path = TAXONOMY_PATH) -> Dict[str, Dict[str, List[str]]]:
    """
    Loads taxonomy from JSON or falls back to TAXONOMY_DATA.
    """
    if input_path.exists():
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return TAXONOMY_DATA


def normalize_skill(skill: str) -> Optional[str]:
    """
    Normalizes a skill name or alias into its canonical form.
    Returns None if not recognized.
    """
    alias_map = build_alias_map(TAXONOMY_DATA)
    return alias_map.get(skill.lower().strip(), None)


if __name__ == "__main__":
    export_taxonomy()
    alias_map = build_alias_map(TAXONOMY_DATA)
    total_canonical = sum(len(skills) for skills in TAXONOMY_DATA.values())
    total_aliases = len(alias_map)
    print("\n=== SKILLS TAXONOMY SUMMARY ===")
    print(f"Categories:       {len(TAXONOMY_DATA)}")
    print(f"Canonical Skills: {total_canonical}")
    print(f"Total Aliases:    {total_aliases}")
    print("\nVerified Alias Normalization Tests:")
    test_cases = [
        "core java", "j2ee", 
        "data analytics", "analytics", 
        "business analysis", 
        "k8s", "react.js", "sklearn"
    ]
    for tc in test_cases:
        print(f"  '{tc:<18}' -> {normalize_skill(tc)}")
