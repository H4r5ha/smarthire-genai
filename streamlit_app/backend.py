"""Application services used by the Streamlit UI."""
from __future__ import annotations

from typing import Any

from src.core.paths import JOBS_CSV, REPORTS_DIR, RESUMES_DIR, VECTOR_DIR
from src.data.loader import dataset_metrics, load_jobs
from src import config
from src.generate.cv_suggestions import generate as generate_cv
from src.mentor.rag_chain import ask as mentor_ask, status as mentor_status
from src.parsing.resume_parser import parse_resume as parse_real_resume
from src.search.job_search import (
    ensure_index_ready,
    rebuild_index as rebuild_real_index,
    search as search_real,
    suggest_roles as suggest_real_roles,
)
from src.evaluate import run_evaluation as evaluate_real
from . import sample_data as sd


class BackendError(Exception):
    pass


class _LocalResumeFile:
    """Small UploadedFile-compatible wrapper for a resume stored on disk."""

    def __init__(self, path):
        self.name = path.name
        self._content = path.read_bytes()

    def getbuffer(self):
        return memoryview(self._content)


def _sample_resume_path():
    """Return a real sample PDF from data/resumes.

    `resume.pdf` is preferred when present so the default is stable; otherwise
    the first PDF in deterministic filename order is used. No candidate fields
    are hard-coded here - the normal resume parser extracts them from the file.
    """
    if not RESUMES_DIR.exists():
        raise BackendError(f'Sample resume directory not found: {RESUMES_DIR}')

    preferred = RESUMES_DIR / 'resume.pdf'
    if preferred.is_file():
        return preferred

    sample_pdfs = sorted(
        path for path in RESUMES_DIR.iterdir()
        if path.is_file() and path.suffix.lower() == '.pdf'
    )
    if not sample_pdfs:
        raise BackendError(f'No sample resume PDFs found in {RESUMES_DIR}')

    return sample_pdfs[0]


def _parse_sample_resume() -> dict:
    """Parse a real sample resume PDF with the same pipeline as an upload."""
    sample_path = _sample_resume_path()
    profile = parse_real_resume(_LocalResumeFile(sample_path))
    profile['source'] = 'sample'
    profile['source_file'] = sample_path.name
    return profile


def parse_resume(file: Any, *, demo: bool = False) -> dict:
    try:
        if demo:
            return _parse_sample_resume()
        return parse_real_resume(file)
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def suggest_roles(profile: dict | None) -> list[dict]:
    try:
        return suggest_real_roles(profile)
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def search_jobs(query: str, profile: dict | None) -> dict:
    try:
        return search_real(query, profile)
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def improve_cv(resume: dict | None, target_job: dict) -> dict:
    if not resume:
        raise BackendError('Upload and parse a resume before generating CV suggestions.')
    try:
        return generate_cv(resume, target_job)
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def ask_mentor(question: str, profile: dict | None, history: list[dict], context: dict | None = None) -> dict:
    try:
        return mentor_ask(question, profile, history, context=context)
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def get_mentor_status() -> dict:
    return mentor_status()


def get_dataset_metrics() -> dict:
    try:
        return {**dataset_metrics(), 'source': 'live'}
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def prepare_index() -> dict:
    try:
        return ensure_index_ready()
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def get_index_status() -> list[dict]:
    index_ready = (
        (VECTOR_DIR / 'jobs_metadata.json').exists()
        and (
            (VECTOR_DIR / 'jobs.index').exists()
            or (VECTOR_DIR / 'jobs.npy').exists()
        )
    )
    metrics = get_dataset_metrics()
    return [
        {
            'name': 'FAISS Index',
            'ready': index_ready,
            'detail': (
                f'{metrics["total_jobs"]:,} job vectors '
                '(auto-built when missing)'
                if index_ready
                else 'Will auto-build from committed CSV'
            ),
        },
        {
            'name': 'Embedding Model',
            'ready': index_ready,
            'detail': (
                f'{config.EMBEDDING_PROVIDER} (low-memory mode)'
                if index_ready
                else f'{config.EMBEDDING_PROVIDER} (created during index build)'
            ),
        },
        {
            'name': 'Job Metadata',
            'ready': index_ready,
            'detail': 'Normalised local Naukri sample',
        },
        {
            'name': 'Career Knowledge Base',
            'ready': True,
            'detail': 'Local career notes loaded',
        },
    ]


def rebuild_index() -> dict:
    try:
        return rebuild_real_index()
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def refresh_data() -> dict:
    try:
        jobs = load_jobs(JOBS_CSV)
        return {
            'ok': True,
            'message': (
                f'Dataset refreshed: {len(jobs):,} valid records detected. '
                'Rebuild the index if the CSV changed.'
            ),
        }
    except Exception as exc:
        raise BackendError(str(exc)) from exc


def run_evaluation() -> dict:
    try:
        result = evaluate_real()
        result['source'] = 'live'
        from src.evaluate import write_report

        write_report(result, REPORTS_DIR / 'answer_quality.md')
        return result
    except Exception as exc:
        raise BackendError(str(exc)) from exc