from __future__ import annotations

import json
import re
from functools import lru_cache

import numpy as np

try:
    import faiss  # type: ignore[import-not-found]
except Exception:
    faiss = None

from .. import config
from ..core.paths import EMBEDDING_META, FAISS_INDEX, JOB_META, JOBS_CSV
from ..data.loader import JobRecord, dataset_metrics, load_jobs
from .embed import embed_texts, fit_and_embed_texts


# ---------------------------------------------------------------------------
# Index management
# ---------------------------------------------------------------------------


def _job_text(job: JobRecord) -> str:
    return job.text


def _has_saved_index() -> bool:
    if not JOB_META.exists():
        return False
    return FAISS_INDEX.exists() or FAISS_INDEX.with_suffix('.npy').exists()


def _index_is_stale() -> bool:
    """Return True when the saved vectorstore was built before the CSV.

    This prevents a particularly confusing class of bugs where the CSV has
    been updated but the application continues searching an older FAISS index.
    """
    if not _has_saved_index() or not JOBS_CSV.exists():
        return False
    try:
        return JOB_META.stat().st_mtime < JOBS_CSV.stat().st_mtime
    except OSError:
        return False


def _build_index() -> tuple[object, list[JobRecord]]:
    jobs = load_jobs(JOBS_CSV)
    if not jobs:
        raise RuntimeError(f'No valid jobs were found in {JOBS_CSV}.')

    vectors, embedding_info = fit_and_embed_texts([_job_text(j) for j in jobs])
    metadata = [j.__dict__ for j in jobs]

    JOB_META.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    EMBEDDING_META.write_text(json.dumps(embedding_info, indent=2), encoding='utf-8')

    if faiss is not None:
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        faiss.write_index(index, str(FAISS_INDEX))
        npy_path = FAISS_INDEX.with_suffix('.npy')
        if npy_path.exists():
            npy_path.unlink()
        return index, jobs

    np.save(FAISS_INDEX.with_suffix('.npy'), vectors)
    if FAISS_INDEX.exists():
        FAISS_INDEX.unlink()
    return vectors, jobs


@lru_cache(maxsize=1)
def load_index() -> tuple[object, list[JobRecord]]:
    """Load the current index, rebuilding it when the CSV has changed."""
    if _has_saved_index() and not _index_is_stale():
        metadata = json.loads(JOB_META.read_text(encoding='utf-8'))
        jobs = [JobRecord(**m) for m in metadata]

        if FAISS_INDEX.exists():
            if faiss is not None:
                return faiss.read_index(str(FAISS_INDEX)), jobs
            load_index.cache_clear()
            return _build_index()

        return np.load(FAISS_INDEX.with_suffix('.npy')), jobs

    return _build_index()


def rebuild_index() -> dict:
    load_index.cache_clear()
    index, jobs = _build_index()
    del index
    load_index.cache_clear()
    load_index()
    backend = 'FAISS' if faiss is not None and FAISS_INDEX.exists() else 'NumPy exact cosine'
    return {
        'ok': True,
        'message': f'Index rebuilt for {len(jobs):,} jobs using {backend}.',
    }


def ensure_index_ready() -> dict:
    try:
        had_artifact = _has_saved_index() and not _index_is_stale()
        _, jobs = load_index()
        backend = 'FAISS' if faiss is not None and FAISS_INDEX.exists() else 'NumPy exact cosine'
        return {
            'ok': True,
            'jobs': len(jobs),
            'backend': backend,
            'built_automatically': not had_artifact,
        }
    except Exception as exc:
        return {
            'ok': False,
            'jobs': 0,
            'backend': None,
            'built_automatically': False,
            'error': str(exc),
        }


def _search_vectors(index: object, query_vector: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    if k <= 0:
        return np.array([], dtype=float), np.array([], dtype=int)
    if faiss is not None and hasattr(index, 'search'):
        scores, idx = index.search(query_vector, k)
        return scores[0], idx[0]
    sims = index @ query_vector[0]
    order = np.argsort(-sims)[:k]
    return sims[order], order


# ---------------------------------------------------------------------------
# Skill normalisation and role-family rules
# ---------------------------------------------------------------------------


def _normalize_skill(text: str) -> str:
    """Normalise a technology name without collapsing C/C++/C# together."""
    value = str(text or '').strip().lower()
    value = value.replace('++', 'plusplus')
    value = value.replace('#', 'sharp')
    value = re.sub(r'\breact\s*\.?(?:js)?\b', 'reactjs', value)
    value = re.sub(r'\bnode\s*\.?(?:js)?\b', 'nodejs', value)
    value = re.sub(r'\bjava\s*script\b', 'javascript', value)
    value = re.sub(r'\btype\s*script\b', 'typescript', value)
    value = re.sub(r'\bmy\s*-?\s*sql\b', 'mysql', value)
    value = re.sub(r'\bms\s*-?\s*sql\b', 'mssql', value)
    value = re.sub(r'\bgoogle\s+cloud\s+platform(?:\s*\(\s*gcp\s*\))?\b', 'gcp', value)
    value = re.sub(r'\bgcp\s+ai\s+platform\b', 'gcp', value)
    value = re.sub(r'\baws\s+sagemaker\b', 'awssagemaker', value)
    value = re.sub(r'\bazure\s+ml\s+studio\b', 'azuremlstudio', value)
    value = re.sub(r'\bazure\s+ml\b', 'azureml', value)
    return re.sub(r'[^a-z0-9]', '', value)


def _skill_map_from_list(skills: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in skills or []:
        label = str(raw).strip()
        key = _normalize_skill(label)
        if key and key not in out:
            out[key] = label
    return out


def _skill_map_from_csv(skills_field: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in (skills_field or '').split(','):
        label = raw.strip()
        key = _normalize_skill(label)
        if key and key not in out:
            out[key] = label
    return out


def _role_key(role: str) -> str:
    return _normalize_skill(role)


# Candidate skill aliases used for role gates. A role gate is deliberately
# stricter than semantic similarity: a vendor-specific role requires the
# vendor technology to exist on the resume.
ROLE_ANY_SKILL_GATES: dict[str, set[str]] = {
    'awsdataengineer': {'aws'},
    'gcpdataengineer': {'gcp'},
    'azuredataengineer': {'azure', 'microsoftazure', 'azureml'},
    'pythondeveloper': {'python'},
    'javadeveloper': {'java'},
    'phpdeveloper': {'php'},
    'reactjsdeveloper': {'reactjs'},
    'frontenddeveloper': {'html5', 'html', 'css3', 'css', 'javascript', 'typescript', 'reactjs'},
    'backenddeveloper': {'python', 'java', 'php', 'nodejs', 'golang', 'rubyrubyonrails', 'rubyrails', 'restapi', 'mongodb', 'sql'},
    'devopsengineer': {'devops', 'jenkins', 'ansible', 'kubernetes', 'terraform', 'docker'},
    'qaengineer': {'selenium', 'appium', 'softwaretesting', 'automationtesting'},
    'automationtester': {'selenium', 'appium', 'cucumber', 'automationtesting', 'uft'},
    'iosdeveloper': {'ios', 'swift'},
    'androiddeveloper': {'android', 'kotlin'},
    'flutterdeveloper': {'flutter', 'dart'},
}

# Explicit role requirements. Tuples are (minimum direct skill matches,
# required-any gate). This determines whether a posting is actually eligible
# for suggestion/search, rather than merely semantically similar.
ROLE_MIN_MATCHES: dict[str, int] = {
    'awsdataengineer': 2,
    'gcpdataengineer': 2,
    'azuredataengineer': 2,
    'dataengineer': 2,
    'bigdataengineer': 2,
    'seniordataengineer': 2,
    'datascientist': 2,
    'seniordatascientist': 2,
    'leaddatascientist': 2,
    'machinelearningengineer': 2,
    'mlengineer': 2,
    'dataanalyst': 1,
    'businessanalyst': 1,
    'softwareengineer': 1,
    'seniorsoftwareengineer': 1,
    'softwaredevelopmentengineer': 1,
    'applicationdeveloper': 1,
    'reactjsdeveloper': 1,
    'pythondeveloper': 1,
    'javadeveloper': 1,
    'phpdeveloper': 1,
    'backenddeveloper': 2,
    'frontenddeveloper': 1,
    'devopsengineer': 1,
    'qaengineer': 1,
    'automationtester': 1,
    'iosdeveloper': 1,
    'androiddeveloper': 1,
    'flutterdeveloper': 1,
    'mobileappdeveloper': 1,
    'reactnativedeveloper': 1,
    'cloudengineer': 1,
    'dataarchitect': 2,
}


def _role_family_jobs(role: str, jobs: list[JobRecord]) -> list[JobRecord]:
    """Return ONLY the exact role family requested by the user.

    This is intentionally title/category based. Searching for "Python
    Developer" must never return a GCP Data Engineer merely because both jobs
    contain Python/BigQuery.
    """
    key = _role_key(role)

    exact_titles = {
        _role_key(j.title): j.title
        for j in jobs
        if j.title and _role_key(j.title)
    }

    # An exact title selection is the strongest filter and handles case
    # differences such as "Aws Data Engineer" vs "AWS Data Engineer".
    if key in exact_titles:
        return [j for j in jobs if _role_key(j.title) == key]

    # For broad categories that are represented through multiple seniority
    # variants, include only that logical family — never vendor variants.
    family_prefixes = {
        'softwareengineer': {'softwareengineer', 'seniorsoftwareengineer'},
        'datascientist': {'datascientist', 'seniordatascientist', 'leaddatascientist'},
        'dataengineer': {'dataengineer', 'seniordataengineer'},
        'machinelearningengineer': {'machinelearningengineer', 'mlengineer'},
    }
    allowed = family_prefixes.get(key)
    if allowed:
        return [j for j in jobs if _role_key(j.title) in allowed]

    return []


def _candidate_job_match(profile_skills: list[str], job: JobRecord) -> dict:
    candidate_map = _skill_map_from_list(profile_skills)
    job_map = _skill_map_from_csv(job.skills)
    matched_keys = set(candidate_map) & set(job_map)
    return {
        'matched_keys': matched_keys,
        'matching': sorted((job_map[k] for k in matched_keys), key=str.casefold),
        'missing': sorted((job_map[k] for k in set(job_map) - matched_keys), key=str.casefold),
    }


def _role_is_skill_grounded(role: str, profile_skills: list[str]) -> bool:
    """Check the candidate has the role's mandatory technology anchor."""
    keys = set(_skill_map_from_list(profile_skills))
    role_key = _role_key(role)

    if role_key in {'datascientist', 'seniordatascientist', 'leaddatascientist'}:
        # Python/NumPy/scikit-learn/TensorFlow/etc. are meaningful anchors.
        return bool(keys & {'python', 'tensorflow', 'pytorch', 'sklearn', 'scikitlearn', 'machinelearning'})

    if role_key in {'machinelearningengineer', 'mlengineer'}:
        return 'python' in keys and bool(
            keys & {'machinelearning', 'ml', 'deeplearning', 'tensorflow', 'pytorch', 'sklearn', 'scikitlearn'}
        )

    if role_key in {'dataengineer', 'seniordataengineer', 'bigdataengineer'}:
        return bool(
            keys & {
                'python', 'sql', 'pyspark', 'spark', 'etl', 'dataengineering',
                'datapipeline', 'datamodeling', 'datawarehousing', 'bigdata', 'bigquery',
            }
        )

    gate = ROLE_ANY_SKILL_GATES.get(role_key)
    if gate:
        return bool(keys & gate)

    # Generic software/application roles require at least one direct skill with
    # an actual job in that family; this is evaluated later at job level.
    return True


def _job_qualifies_for_role(role: str, profile_skills: list[str], job: JobRecord) -> bool:
    if not _role_is_skill_grounded(role, profile_skills):
        return False

    role_key = _role_key(role)
    candidate_keys = set(_skill_map_from_list(profile_skills))
    job_keys = set(_skill_map_from_csv(job.skills))
    matched = candidate_keys & job_keys
    min_matches = ROLE_MIN_MATCHES.get(role_key, 1)

    # Cloud-specific data-engineering roles require BOTH the cloud anchor and
    # enough additional direct skills to show a real data-engineering fit.
    if role_key in {'awsdataengineer', 'gcpdataengineer', 'azuredataengineer'}:
        cloud_gate = ROLE_ANY_SKILL_GATES[role_key]
        if not candidate_keys & cloud_gate:
            return False
        return len(matched) >= min_matches

    # Python/Java/etc. developer roles may legitimately match on one core
    # language because that language is itself the role-defining skill.
    return len(matched) >= min_matches


def _role_qualified_jobs(role: str, profile_skills: list[str], jobs: list[JobRecord]) -> list[JobRecord]:
    return [j for j in _role_family_jobs(role, jobs) if _job_qualifies_for_role(role, profile_skills, j)]


def _profile_text(profile: dict) -> str:
    return ' '.join(
        [
            str(profile.get('target_role', '')),
            str(profile.get('summary', '')),
            *[str(x) for x in profile.get('skills', [])],
        ]
    ).strip()


def _cosine_profile_scores(profile: dict, jobs: list[JobRecord]) -> dict[str, float]:
    text = _profile_text(profile)
    if not text or not jobs:
        return {j.job_id: 0.0 for j in jobs}
    vectors = embed_texts([text] + [j.text for j in jobs])
    profile_vec = vectors[0]
    return {
        job.job_id: float(profile_vec @ job_vec)
        for job, job_vec in zip(jobs, vectors[1:])
    }


def _fit_score(profile: dict, job: JobRecord, profile_semantic: float) -> tuple[float, dict]:
    match = _candidate_job_match(profile.get('skills', []), job)
    matched_keys = match['matched_keys']
    job_map = _skill_map_from_csv(job.skills)
    candidate_key_count = max(1, len(_skill_map_from_list(profile.get('skills', []))))
    required_count = max(1, len(job_map))

    # Direct skills are the primary signal. Semantic similarity is intentionally
    # secondary so words like "data" or "engineering" cannot overwhelm real
    # skill evidence.
    coverage = len(matched_keys) / required_count
    candidate_usage = len(matched_keys) / candidate_key_count
    direct = 0.75 * coverage + 0.25 * min(candidate_usage * 4.0, 1.0)
    fit = 0.80 * direct + 0.20 * max(0.0, min(profile_semantic, 1.0))

    return max(0.0, min(0.99, fit)), match


# ---------------------------------------------------------------------------
# Job search
# ---------------------------------------------------------------------------


def _normalised_query_is_role(query: str, jobs: list[JobRecord]) -> str | None:
    key = _role_key(query)
    if not key:
        return None

    exact = {}
    for job in jobs:
        job_key = _role_key(job.title)
        if job_key:
            exact[job_key] = job.title
    if key in exact:
        return exact[key]

    aliases = {
        'softwareengineer': 'Software Engineer',
        'datascientist': 'Data Scientist',
        'dataanalyst': 'Data Analyst',
        'dataengineer': 'Data Engineer',
        'seniordataengineer': 'Senior Data Engineer',
        'awsdataengineer': 'AWS Data Engineer',
        'azuredataengineer': 'Azure Data Engineer',
        'gcpdataengineer': 'GCP Data Engineer',
        'pythondeveloper': 'Python Developer',
        'javadeveloper': 'Java Developer',
        'backenddeveloper': 'Backend Developer',
        'frontenddeveloper': 'Frontend Developer',
        'reactjsdeveloper': 'React JS Developer',
        'machinelearningengineer': 'Machine Learning Engineer',
        'mlengineer': 'ML Engineer',
    }
    title = aliases.get(key)
    return title if title and _role_key(title) in exact else None


def _result_dict(job: JobRecord, profile: dict | None, profile_semantic: float) -> dict:
    if profile:
        score, match = _fit_score(profile, job, profile_semantic)
        percent = round(score * 100)
        matching = match['matching'][:8]
        missing = match['missing'][:8]
        why = (
            f'{len(match["matched_keys"])} of {len(_skill_map_from_csv(job.skills))} listed skills found on your resume; '
            f'profile similarity {profile_semantic:.2f}.'
        )
    else:
        percent = max(0, min(99, round(profile_semantic * 100)))
        matching = []
        missing = []
        why = f'Semantic similarity to your search: {profile_semantic:.2f}. Upload a resume for a personalised match score.'

    return {
        'job_id': job.job_id,
        'title': job.title,
        'company': job.company,
        'location': job.location,
        'mode': 'Not specified',
        'type': 'Job',
        'posted': 'Dataset record',
        'score': percent,
        'matching': matching,
        'missing': missing,
        'why': why,
        'experience': job.experience,
        'salary': job.salary,
        'skills': job.skills,
        'description': job.description,
        'url': job.url,
        'category': job.category,
    }


def search(query: str, profile: dict | None = None, k: int | None = None) -> dict:
    index, jobs = load_index()
    query = (query or '').strip()
    if not query and not profile:
        return {'summary': None, 'jobs': [], 'source': 'live'}

    profile = profile or {}
    top_k = max(1, min(k or config.TOP_K_JOBS, len(jobs)))
    selected_role = _normalised_query_is_role(query, jobs) if query else None

    # ------------------------------------------------------------------
    # IMPORTANT: a role selection is NOT a global semantic search.
    # ------------------------------------------------------------------
    # This fixes the bug where clicking "Python Developer" returned a
    # "GCP Data Engineer". Once a role is selected, retrieval is restricted to
    # that role family first, and only then are the eligible jobs ranked.
    if selected_role:
        role_jobs = _role_family_jobs(selected_role, jobs)

        if profile:
            eligible_jobs = _role_qualified_jobs(selected_role, profile.get('skills', []), jobs)
            if not eligible_jobs:
                return {
                    'summary': {
                        'relevant_jobs': 0,
                        'best_match': '0%',
                        'avg_match': '0%',
                        'filters': f'Role: {selected_role}',
                    },
                    'jobs': [],
                    'source': 'live',
                }
            semantics = _cosine_profile_scores(profile, eligible_jobs)
            results = [
                _result_dict(job, profile, semantics.get(job.job_id, 0.0))
                for job in eligible_jobs
            ]
        else:
            # No profile: use semantic retrieval only inside the requested role.
            if not role_jobs:
                return {'summary': None, 'jobs': [], 'source': 'live'}
            query_vec = embed_texts([query])[0]
            job_vecs = embed_texts([j.text for j in role_jobs])
            scores = job_vecs @ query_vec
            order = np.argsort(-scores)[:top_k]
            results = [
                _result_dict(role_jobs[int(i)], None, float(scores[int(i)]))
                for i in order
            ]

        results.sort(key=lambda item: (-item['score'], item['title'].casefold(), item['job_id']))
        results = results[:top_k]
        scores = [r['score'] for r in results]
        return {
            'summary': {
                # For a selected role, every returned job is already compatible.
                # Do NOT count arbitrary score thresholds separately from the
                # eligibility rules, because that was the source of "0 relevant
                # jobs" while a role was still displayed as recommended.
                'relevant_jobs': len(results),
                'best_match': f'{scores[0]}%' if scores else '0%',
                'avg_match': f'{round(sum(scores) / len(scores))}%' if scores else '0%',
                'filters': f'Role: {selected_role}',
            },
            'jobs': results,
            'source': 'live',
        }

    # ------------------------------------------------------------------
    # Free-form search: preserve semantic retrieval, but keep fit scoring
    # skill-grounded when a resume exists.
    # ------------------------------------------------------------------
    profile_skill_map = _skill_map_from_list(profile.get('skills', []))
    has_profile = bool(profile_skill_map or profile.get('summary') or profile.get('target_role'))
    profile_text = _profile_text(profile)

    if query:
        query_vector = embed_texts([query])[0]
        if profile_text:
            profile_vector = embed_texts([profile_text])[0]
            vector = (0.80 * query_vector + 0.20 * profile_vector).reshape(1, -1)
            norm = float(np.linalg.norm(vector))
            if norm > 0:
                vector = vector / norm
        else:
            vector = query_vector.reshape(1, -1)
    else:
        vector = embed_texts([profile_text])[0].reshape(1, -1)

    retrieval_scores, indices = _search_vectors(index, vector, top_k)
    candidate_jobs: list[JobRecord] = []
    ordered_scores: list[float] = []
    for score, idx in zip(retrieval_scores, indices):
        idx = int(idx)
        if 0 <= idx < len(jobs):
            candidate_jobs.append(jobs[idx])
            ordered_scores.append(float(score))

    semantics = _cosine_profile_scores(profile, candidate_jobs) if has_profile else {}
    results = []
    for rel_score, job in zip(ordered_scores, candidate_jobs):
        result = _result_dict(job, profile if has_profile else None, semantics.get(job.job_id, rel_score))
        result['_retrieval'] = rel_score
        results.append(result)

    results.sort(key=lambda item: (-item['score'], item['title'].casefold(), item['job_id']))
    results = results[:top_k]

    scores = [r['score'] for r in results]
    relevant = sum(score >= 50 for score in scores)
    for r in results:
        r.pop('_retrieval', None)

    return {
        'summary': {
            'relevant_jobs': relevant,
            'best_match': f'{scores[0]}%' if scores else '0%',
            'avg_match': f'{round(sum(scores) / len(scores))}%' if scores else '0%',
            'filters': 'None',
        },
        'jobs': results,
        'source': 'live',
    }


# ---------------------------------------------------------------------------
# Suggested roles
# ---------------------------------------------------------------------------


def _all_role_titles(jobs: list[JobRecord]) -> list[str]:
    """Use the dataset as the source of truth for available role families."""
    seen: dict[str, str] = {}
    for job in jobs:
        title = (job.title or '').strip()
        key = _role_key(title)
        if title and key:
            seen.setdefault(key, title)
    return list(seen.values())


def _role_score(profile: dict, role: str, qualified_jobs: list[JobRecord]) -> tuple[float, str]:
    """Return the same compatibility score the user sees after selecting the role.

    The suggested-role ranking and the selected-role ``Best Match`` must use the
    same metric. Previously the role card used a weighted combination of the best
    and second-best postings plus a target-role bonus, while the selected-role
    page displayed the best individual posting score. That made a lower-ranked
    role appear to have a higher match percentage after selection.

    The ranking metric is now exactly the best compatible job's fit score. This
    makes the ordering and the later ``Best Match`` value mathematically
    consistent. No target-role bonus is applied here because it would be a
    preference signal, not a compatibility score.
    """
    if not qualified_jobs:
        return 0.0, ''

    semantics = _cosine_profile_scores(profile, qualified_jobs)
    scored_jobs = []
    for job in qualified_jobs:
        fit, match = _fit_score(profile, job, semantics.get(job.job_id, 0.0))
        scored_jobs.append((fit, len(match['matched_keys']), job))

    # The exact same best-posting score is what appears as ``Best Match`` when
    # the user selects this role. Tie-break using direct skill matches, then job ID
    # for deterministic ordering.
    scored_jobs.sort(key=lambda x: (-x[0], -x[1], x[2].job_id))
    best_fit, best_matches, _ = scored_jobs[0]

    skill_word = 'skill' if best_matches == 1 else 'skills'
    job_word = 'job' if len(qualified_jobs) == 1 else 'jobs'
    reason = (
        f'Direct skill match: {best_matches} matching {skill_word} on the strongest compatible '
        f'{role} posting; {len(qualified_jobs)} compatible {job_word} in the corpus; '
        f'best compatibility score {round(best_fit * 100)}%.'
    )
    return best_fit, reason


def suggest_roles(profile: dict | None) -> list[dict]:
    jobs = load_jobs(JOBS_CSV)
    if not profile:
        metrics = dataset_metrics()
        return [
            {'role': 'Software Engineer', 'jobs': metrics.get('se_jobs', 0), 'reason': 'Available in the local job corpus.'},
            {'role': 'Data Scientist', 'jobs': metrics.get('ds_jobs', 0), 'reason': 'Available in the local job corpus.'},
        ]

    profile_skills = [str(x) for x in profile.get('skills', [])]
    scored: list[dict] = []

    # The dataset, not a hard-coded four-role list, determines which role names
    # are actually available. Exact title matching also keeps AWS/GCP/Azure and
    # seniority variants separate.
    for role in _all_role_titles(jobs):
        qualified = _role_qualified_jobs(role, profile_skills, jobs)
        if not qualified:
            continue

        score, reason = _role_score(profile, role, qualified)
        scored.append({
            'role': role,
            'jobs': len(qualified),
            'reason': reason,
            '_score': score,
        })

    scored.sort(key=lambda item: (-item['_score'], item['role'].casefold()))
    for item in scored:
        item.pop('_score', None)

    return scored[:3]


@lru_cache(maxsize=1)
def _autocomplete_catalog() -> tuple[str, ...]:
    jobs = load_jobs(JOBS_CSV)
    titles = {str(j.title).strip() for j in jobs if str(j.title).strip()}
    return tuple(sorted(titles, key=lambda value: (len(value), value.lower())))


def autocomplete(query: str, limit: int = 8) -> list[str]:
    text = (query or '').strip().lower()
    if not text:
        return []
    catalog = _autocomplete_catalog()
    prefix = [title for title in catalog if title.lower().startswith(text)]
    contains = [title for title in catalog if text in title.lower() and title not in prefix]
    normalised = text.replace('/', ' ').replace('-', ' ')
    tokens = [token for token in normalised.split() if token]
    token_matches = [
        title for title in catalog
        if all(token in title.lower().replace('/', ' ').replace('-', ' ') for token in tokens)
        and title not in prefix and title not in contains
    ]
    return (prefix + contains + token_matches)[:max(1, int(limit))]