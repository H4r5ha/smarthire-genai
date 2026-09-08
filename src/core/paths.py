from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / 'data'
JOBS_DIR = DATA_DIR / 'jobs'
CAREER_NOTES_DIR = DATA_DIR / 'career_notes'
RESUMES_DIR = DATA_DIR / 'resumes'
VECTOR_DIR = ROOT / 'vectorstore'
EMBEDDING_MODEL_DIR = VECTOR_DIR / 'embedding_model'
REPORTS_DIR = ROOT / 'reports'

JOBS_CSV = JOBS_DIR / 'smarthire_jobs_80.csv'
FAISS_INDEX = VECTOR_DIR / 'jobs.index'
JOB_META = VECTOR_DIR / 'jobs_metadata.json'
EMBEDDING_META = VECTOR_DIR / 'embedding_meta.json'

for d in (VECTOR_DIR, EMBEDDING_MODEL_DIR, REPORTS_DIR, CAREER_NOTES_DIR):
    d.mkdir(parents=True, exist_ok=True)