from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..core.paths import JOBS_CSV

REQUIRED_COLUMNS = {
    'job_id', 'category', 'title', 'company', 'location', 'experience',
    'salary', 'skills', 'description', 'jdURL'
}


@dataclass(frozen=True)
class JobRecord:
    job_id: str
    category: str
    title: str
    company: str
    location: str
    experience: str
    salary: str
    skills: str
    description: str
    url: str

    @property
    def text(self) -> str:
        return (
            f'Title: {self.title}\nCategory: {self.category}\nCompany: {self.company}\n'
            f'Location: {self.location}\nExperience: {self.experience}\nSkills: {self.skills}\n'
            f'Description: {self.description}'
        )


def _clean(value: object) -> str:
    text = '' if value is None else str(value)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def load_jobs(path: Path = JOBS_CSV) -> list[JobRecord]:
    if not path.exists():
        raise FileNotFoundError(f'Job dataset not found: {path}')
    df = pd.read_csv(path, low_memory=False).fillna('')
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f'Dataset is missing required columns: {sorted(missing)}')
    jobs: list[JobRecord] = []
    seen: set[str] = set()
    for row in df.to_dict('records'):
        jid = _clean(row['job_id'])
        desc = _clean(row['description'])
        if not jid or not desc or jid in seen:
            continue
        seen.add(jid)
        jobs.append(JobRecord(
            job_id=jid,
            category=_clean(row['category']) or 'Other',
            title=_clean(row['title']) or 'Untitled role',
            company=_clean(row['company']) or 'Unknown company',
            location=_clean(row['location']) or 'Not specified',
            experience=_clean(row['experience']) or 'Not specified',
            salary=_clean(row['salary']) or 'Not disclosed',
            skills=_clean(row['skills']),
            description=desc,
            url=_clean(row['jdURL']),
        ))
    return jobs


def dataset_metrics(path: Path = JOBS_CSV) -> dict:
    jobs = load_jobs(path)
    counts = {}
    for j in jobs:
        counts[j.category] = counts.get(j.category, 0) + 1
    return {
        'total_jobs': len(jobs),
        'ds_jobs': counts.get('Data Scientist', 0),
        'se_jobs': counts.get('Software Engineer', 0),
        'valid': len(jobs),
    }
