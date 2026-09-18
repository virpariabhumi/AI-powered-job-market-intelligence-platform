import json
import pandas as pd
from pathlib import Path

DATA_PATH = Path('data/cleaned/india_jobs_cleaned.csv')
NOTEBOOK_PATH = Path('notebooks/data_exploration.ipynb')

df = pd.read_csv(DATA_PATH)
total_rows = len(df)

print('==================================================')
print(f'   DATASET PROFILING REPORT ({total_rows:,} POSTINGS)')
print('==================================================\n')

# 1. Missing Values
print('1. MISSING VALUES PER COLUMN:')
missing = df.isnull().sum()
missing_pct = (missing / total_rows) * 100
missing_df = pd.DataFrame({'Missing': missing, 'Percent (%)': missing_pct.round(2)})
print(missing_df[missing_df['Missing'] > 0])
print()

# 2. Top Job Titles
print('2. TOP 10 JOB TITLES:')
print(df['title'].value_counts().head(10))
print()

# 3. Top Locations
print('3. TOP 10 LOCATIONS:')
print(df['location'].value_counts().head(10))
print()

# 4. Top Experience Levels
print('4. TOP 5 EXPERIENCE LEVELS:')
print(df['formatted_experience_level'].value_counts().head(5))
print()

# 5. Top Skills in key_skills
print('5. TOP 15 SKILLS MENTIONED IN key_skills:')
all_skills = (
    df['key_skills']
    .dropna()
    .str.split(',')
    .explode()
    .str.strip()
    .str.lower()
)
all_skills = all_skills[all_skills != '']
top_skills = all_skills.value_counts().head(15)
print(top_skills)
print()

# 6. Description word counts
word_counts = df['description'].fillna('').apply(lambda x: len(x.split()))
print('6. JOB DESCRIPTION LENGTH (WORDS):')
print(f'   Median: {word_counts.median():.0f} words')
print(f'   Min:    {word_counts.min():.0f} words | Max: {word_counts.max():.0f} words')
print(f'   Mean:   {word_counts.mean():.1f} words')

# Build interactive Jupyter notebook
nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# AI-Powered Job Market Intelligence: Dataset Exploration (EDA)\n",
                "**Author:** Member 1 - Data & Intelligence Engineer  \n",
                f"**Dataset:** india_jobs_cleaned.csv ({total_rows:,} records)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "\n",
                "df = pd.read_csv('../data/cleaned/india_jobs_cleaned.csv')\n",
                "df.head()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Missing Values Overview"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "missing = df.isnull().sum()\n",
                "missing[missing > 0]"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Top Job Designations"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 4))\n",
                "df['title'].value_counts().head(10).plot(kind='barh', color='teal')\n",
                "plt.title('Top 10 Job Designations')\n",
                "plt.xlabel('Number of Postings')\n",
                "plt.gca().invert_yaxis()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Geographic Distribution (Top Locations)"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 4))\n",
                "df['location'].value_counts().head(10).plot(kind='bar', color='coral')\n",
                "plt.title('Top 10 Job Locations')\n",
                "plt.ylabel('Number of Postings')\n",
                "plt.xticks(rotation=45, ha='right')\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Key Skills Distribution"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "skills = df['key_skills'].dropna().str.split(',').explode().str.strip().str.lower()\n",
                "plt.figure(figsize=(10, 5))\n",
                "skills.value_counts().head(15).plot(kind='barh', color='navy')\n",
                "plt.title('Top 15 Skills in Market')\n",
                "plt.xlabel('Frequency')\n",
                "plt.gca().invert_yaxis()\n",
                "plt.show()"
            ]
        }
    ],
    "metadata": {
        "language_info": {"name": "python", "version": "3"}
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

with open(NOTEBOOK_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=2)

print(f'\nNotebook successfully generated at: {NOTEBOOK_PATH}')
