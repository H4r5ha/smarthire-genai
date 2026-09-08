from __future__ import annotations

import sys
from pathlib import Path

# Allow `python scripts\\build_index.py` from the project root on Windows.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.search.job_search import rebuild_index  # noqa: E402


if __name__ == '__main__':
    print('Building the job index using the configured embedding provider...')
    result = rebuild_index()
    print(result['message'])
