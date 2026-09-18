# Dataset Schema Documentation

## Primary Dataset: india_jobs_cleaned.csv
- **Total Valid Postings**: 12,188
- **Source**: Indian Tech Job Postings (Kaggle / Naukri)
- **File Location**: data/cleaned/india_jobs_cleaned.csv

### Column Definitions

| Column | Data Type | Description | Used By |
| :--- | :--- | :--- | :--- |
| job_id | String | Unique identifier (e.g., 	rain-0, 	est-4) | Primary Key / Indexing |
| 	itle | String | Standardized job role / designation | Role Standardization (W5) |
| description | String | Complete job description text | NLP Skill Extraction (W7) |
| key_skills | String | Comma-separated list of tagged skills | Taxonomy & Graph Co-occurrence |
| ormatted_experience_level | String | Experience range (e.g. 5-7 yrs) | Career Guidance & Filtering |
| location | String | City or region in India | Geographic Insights |
| salary | String | Salary range bracket (if available) | Market Analysis |
| company_name_encoded | String/Int | Encoded employer identifier | Anonymized Company Tracking |
| source_split | String | Original dataset split (	rain or 	est) | Ingestion Lineage |
