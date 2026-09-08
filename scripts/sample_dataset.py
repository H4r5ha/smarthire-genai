from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

import pandas as pd


def clean(value: object) -> str:
    text = html.unescape(str(value or ''))
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def read_source(path: Path, category: str, seen: set[str], need: int) -> pd.DataFrame:
    df = pd.read_csv(path, usecols=['title','companyName','location','experience','salary','jobDescription','tagsAndSkills','jdURL','jobId'], low_memory=False)
    df['job_id'] = df['jobId'].astype(str)
    df = df[df['jobDescription'].fillna('').astype(str).str.strip().ne('')].copy()
    df = df[~df['job_id'].isin(seen)].drop_duplicates('job_id')
    df = df.head(need).copy()
    seen.update(df['job_id'])
    df['category'] = category
    df['title'] = df['title'].map(clean)
    df['company'] = df['companyName'].map(clean).replace('', 'Unknown company')
    df['location'] = df['location'].map(clean).replace('', 'Not specified')
    df['experience'] = df['experience'].map(clean).replace('', 'Not specified')
    df['salary'] = df['salary'].map(clean).replace('', 'Not disclosed')
    df['skills'] = df['tagsAndSkills'].map(clean)
    df['description'] = df['jobDescription'].map(clean)
    return df[['job_id','category','title','company','location','experience','salary','skills','description','jdURL']]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--software', type=Path, required=True)
    ap.add_argument('--data-scientist', type=Path, required=True)
    ap.add_argument('--per-category', type=int, default=500)
    ap.add_argument('--output', type=Path, default=Path('data/jobs/smarthire_jobs_1000.csv'))
    args = ap.parse_args()
    seen: set[str] = set()
    frames = [
        read_source(args.software, 'Software Engineer', seen, args.per_category),
        read_source(args.data_scientist, 'Data Scientist', seen, args.per_category),
    ]
    result = pd.concat(frames, ignore_index=True).drop_duplicates('job_id')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.output, index=False, encoding='utf-8')
    print(f'Wrote {len(result):,} records to {args.output}')
    print(result['category'].value_counts().to_string())


if __name__ == '__main__':
    main()
