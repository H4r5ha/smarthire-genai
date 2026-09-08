from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.paths import JOBS_CSV
from src.search.job_search import load_index

if __name__ == '__main__':
    print(f'CSV: {JOBS_CSV}')
    if not JOBS_CSV.exists():
        raise SystemExit('ERROR: required 80-row CSV is missing.')
    index, jobs = load_index()
    print(f'OK: loaded/built index for {len(jobs):,} jobs.')
    print(f'Index object: {type(index).__name__}')
