import html
import re
from pathlib import Path
import pandas as pd

# Define robust project paths using pathlib
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "cleaned" / "india_jobs_cleaned.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed" / "jobs_cleaned.csv"


def clean_text(text: object) -> str:
    """
    Cleans raw text while carefully preserving technical terms
    (e.g., C++, C#, .NET, Node.js).
    """
    if pd.isna(text):
        return ""
    text_str = str(text)

    # 1. Unescape HTML entities (&amp; -> &, &nbsp; -> space)
    text_str = html.unescape(text_str)

    # 2. Remove HTML tags if present (<p>, <br>, etc.)
    text_str = re.sub(r"<[^>]+>", " ", text_str)

    # 3. Remove ellipsis noise and weird trailing dots
    text_str = re.sub(r"\.{2,}", " ", text_str)

    # 4. Normalize whitespace (tabs, newlines, multiple spaces -> single space)
    text_str = re.sub(r"\s+", " ", text_str).strip()

    return text_str


def clean_skills(skills_str: object) -> str:
    """
    Cleans and deduplicates comma-separated skills.
    Removes empty tokens, ellipsis artifacts, and pure punctuation.
    """
    if pd.isna(skills_str):
        return ""

    raw_tokens = str(skills_str).split(",")
    cleaned_tokens = []
    seen = set()

    for token in raw_tokens:
        t = token.strip().lower()
        # Remove ellipsis artifacts and pure punctuation
        t = re.sub(r"^\.|\.$", "", t).strip()
        
        # Keep only valid non-empty tokens longer than 1 character, or special single letters like 'r' or 'c'
        if t and t not in seen and (len(t) > 1 or t in {"r", "c"}):
            seen.add(t)
            cleaned_tokens.append(t)

    return ", ".join(cleaned_tokens)


def clean_jobs_dataset(
    input_path: Path = DEFAULT_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
) -> pd.DataFrame:
    """
    Main pipeline function to clean the complete job postings dataset.
    """
    print(f"Loading data from: {input_path}")
    df = pd.read_csv(input_path)
    initial_count = len(df)

    # 1. Drop duplicate postings based on core content
    df = df.drop_duplicates(subset=["title", "description", "location"]).copy()

    # 2. Clean text fields
    print("Cleaning job titles and descriptions...")
    df["title"] = df["title"].apply(clean_text).str.lower()
    df["description"] = df["description"].apply(clean_text)

    # 3. Clean and normalize key_skills
    print("Cleaning skills list...")
    df["key_skills"] = df["key_skills"].apply(clean_skills)

    # 4. Clean location and experience
    df["location"] = df["location"].fillna("Not Specified").apply(clean_text)
    df["formatted_experience_level"] = (
        df["formatted_experience_level"].fillna("Not Specified").apply(clean_text)
    )

    # 5. Drop rows where title or description became empty
    df = df[(df["title"] != "") & (df["description"] != "")]

    # 6. Ensure output directory exists and save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"\nData cleaning completed!")
    print(f"Initial rows: {initial_count:,}")
    print(f"Final clean rows: {len(df):,}")
    print(f"Clean master dataset saved to: {output_path}")

    return df


if __name__ == "__main__":
    clean_jobs_dataset()
