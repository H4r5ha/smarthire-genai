# SmartHire GenAI
### Resume Matching & AI Career Mentor

An end-to-end Generative AI career portal — parse a resume, find matching jobs through semantic search, get AI-generated CV improvement suggestions, and chat with a RAG-based AI Career Mentor.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4)
![LangChain](https://img.shields.io/badge/Orchestration-LangChain-1C3C3C)
![FAISS](https://img.shields.io/badge/Vector%20Store-FAISS-lightgrey)

**Live app:** [smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app](https://smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app/)

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Evaluation](#evaluation)
- [Guardrails & Safety](#guardrails--safety)
- [Deployment](#deployment)
- [Limitations](#limitations)

---

## Overview

SmartHire GenAI takes a person from **"here's my resume"** to **"here's how to land this specific job,"** in one guided flow:

| Step | What happens |
|---|---|
| 1. **Upload** | Upload or paste a resume → get a structured, parsed profile |
| 2. **Match** | Compare against a job corpus (or a pasted JD) → get ranked, explainable matches |
| 3. **Improve** | Get an ATS before/after score, a prioritized skill-gap list, and rewritten resume sections |
| 4. **Ask** | Chat with an AI Career Mentor about that resume and job, grounded strictly in retrieved evidence |

> **Note:** In line with LinkedIn's and Naukri's Terms of Service, the app does **not** scrape live job boards. It searches a pre-collected, embedded job dataset instead — a GenAI-native approach to "finding related jobs."

A **Demo / Sample-data mode** toggle in the sidebar fills every page with clearly-labelled sample data, so the full flow can be explored without uploading a real resume.

---

## Features

<details open>
<summary><strong>Page 1 — Resume Upload</strong></summary>

- Accepts **PDF, DOCX, or TXT** resumes, or a built-in sample resume for quick testing.
- **Privacy mode:** upload up to 4 cropped screenshots (PNG/JPG/WEBP, ≤10MB each) instead of a full resume.
- Resume text is parsed by an LLM into a structured, validated JSON profile (name, skills, experience, education, target role).
- A **profile completeness score (0–100%)** is shown with a checklist of exactly what's missing.
- A safety guardrail checks the **extracted resume text itself**, before it ever reaches the LLM.
- Resumes are processed through a temp file, deleted immediately after parsing — nothing persists on disk.
- Resume text is capped at a max length before hitting the LLM, to guard against oversized documents.
- A button at the bottom moves to the Job Match page once parsing is complete.

</details>

<details open>
<summary><strong>Page 2 — Job Match</strong></summary>

- Paste a job description, or search for a role from suggested titles.
- After parsing, the top 3 matching roles are auto-suggested from the resume.
- **Typo-tolerant search:** a non-catalog title like "software developer" still matches, via prefix/substring/token overlap.
- **Two scoring modes:**
  - *Exact role search* — only returns jobs from that strict role family.
  - *Free-text / JD search* — blends semantic similarity with direct skill overlap.
- **Skill normalization:** `React.js` / `React` / `ReactJS`, `MySQL` / `My-SQL`, `C` / `C++` / `C#`, etc. are treated as the same skill.
- **Role gating:** a job only appears if the candidate has that role's mandatory anchor skill (e.g. "Data Scientist" needs Python/ML evidence) — prevents nonsense matches.
- **Soft-skill filtering:** terms like "Project Management" are excluded from both the chips and the match-percentage math.
- Every match card shows a **"why" string** (e.g. *"4 of 9 listed skills found; profile similarity 0.81"*).
- The FAISS index **auto-rebuilds** if the underlying job CSV changed, with a NumPy fallback if FAISS isn't available.
- Pasting a JD triggers a small LLM step to extract a clean job title from the full text (not just the first line), with a heuristic fallback.
- Selecting a role and hitting send moves straight to the CV Improvement page.

</details>

<details open>
<summary><strong>Page 3 — CV Improvement</strong></summary>

- **Before/after ATS scores** that can never drift out of sync with the page:
  - *Before* — computed deterministically from matched/missing skill counts.
  - *After* — a capped projection based on the actual generated content (rewritten bullets, summary, soft skills).
- **Missing skills** grouped by **High / Medium / Low priority**, each its own colour-coded block.
- A dedicated **soft skills** section, separate from the technical skill-gap chips.
- **Section-specific rewrites** — experience bullets, projects, certifications, and achievements are each rewritten individually, not with one generic pass.
- Suggests concrete skills to learn next, to close the gap and raise the ATS score.
- A button at the bottom moves to the AI Career Mentor page.

</details>

<details open>
<summary><strong>Page 4 — AI Career Mentor</strong></summary>

- A **RAG chatbot** scoped strictly to the user's resume and selected job — off-topic questions are declined.
- **Role-aware suggested questions** the user can tap, deterministic per target role.
- A **target-job summary card** stays visible while chatting, so context is never lost.
- **5-step RAG pipeline** — Guardrail → Retrieve → Prompt → Gemini → Output — a real LangChain LCEL chain.
- **Blended retrieval** from two sources: job postings + a separate career-notes knowledge base.
- **Evidence gate:** if retrieved evidence scores too low, the mentor says so instead of guessing.
- **Truncation self-check:** a cut-off answer triggers one automatic retry with a corrective prompt.
- **Natural-length answers** — no rigid "80–140 words, 4 bullets max" template. The mentor matches its structure to the question, staying within a soft ~250-word guideline (with an exception for genuinely multi-part questions).
- **Scope guardrail:** a keyword blocklist plus a prompt-level rule to decline and redirect anything outside career/resume/job-search topics.
- Every answer shows a **relevance score per source** and a **pipeline trace** for transparency.

</details>

<details open>
<summary><strong>System-Level Features</strong></summary>

- **Demo / Sample-data mode** — fills every page with labelled sample data for testing.
- **Sidebar status panel** — live "Ready" / "Online" indicators for the vector index and mentor RAG, plus the candidate's name, target role, and skill count.
- **Two hidden developer pages:** Data & Index Management, and an Evaluation dashboard.
- **Global error handling** — unhandled errors show a friendly message; full tracebacks go only to server logs.
- **Prompt-injection guardrails** — blocks patterns like "ignore previous instructions," "reveal system prompt," and "jailbreak," at every LLM call site.
- **Auto-embedding on first run** — the FAISS index builds itself on startup if missing.

</details>

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM & embeddings | Google Gemini (generation + embeddings), configurable via `.env` |
| Orchestration | LangChain — LCEL chain for the mentor's RAG pipeline |
| Vector store | FAISS, with a NumPy cosine-similarity fallback |
| Document parsing | `pypdf`, `python-docx` |
| Data handling | `pandas`, `numpy`, `scikit-learn` |
| UI | Streamlit |
| Deployment | Streamlit Community Cloud |

---

## Architecture

```
Resume upload (PDF / DOCX / TXT / screenshots)
        │
        ▼
Document loader + chunking
        │
        ▼
LLM structured parser ──► clean JSON profile
        │
        ├──► embed profile ──► FAISS search ──► role-gated, skill-normalized job matches
        │
        ├──► CV improvement prompt ──► priority-grouped skill gaps + section-wise rewrites
        │
        └──► AI Career Mentor: Guardrail ─► Retrieve ─► Prompt ─► Gemini ─► Output
                     (RAG over job corpus + career notes, evidence gate, retry-on-truncation)
        │
   guardrails checked at every LLM call site
        │
        ▼
Streamlit portal ──► GitHub ──► Streamlit Community Cloud
```

---

## Project Structure

<details>
<summary>Click to expand</summary>

```
smarthire-genai/
├── README.md
├── requirements.txt
├── .env.example                  # copy to .env and fill in your Gemini API key
├── .streamlit/
│   ├── config.toml                # theme
│   └── secrets.toml.example       # template for Streamlit Cloud secrets
│
├── data/
│   ├── jobs/                      # pre-collected job dataset (CSV)
│   ├── resumes/                   # sample resumes used by Demo mode
│   └── career_notes/              # role roadmaps / guides retrieved by the mentor
│
├── vectorstore/                   # generated/cached FAISS index + metadata
│
├── notebooks/
│   ├── 01_embeddings_explore.ipynb
│   ├── 02_build_faiss.ipynb
│   └── 03_rag_prototype.ipynb
│
├── src/
│   ├── config.py                  # env/config loading
│   ├── core/                      # shared path helpers
│   ├── data/                      # dataset loading utilities
│   ├── llm/                       # Gemini client wrapper
│   ├── parsing/                   # resume loading + LLM structured-output parser
│   ├── search/                    # embeddings + FAISS-backed job search
│   ├── generate/                  # prompt library + CV improvement generator
│   ├── mentor/                    # LangChain RAG chain for the AI Career Mentor
│   ├── safety/                    # guardrails (off-topic, prompt-injection, safety checks)
│   └── evaluate.py                # retrieval/answer-quality evaluation helpers
│
├── streamlit_app/
│   ├── app.py                     # Streamlit entry point / page router
│   ├── backend.py                 # glue between UI and src/ pipeline
│   ├── state.py, sidebar.py, styles.py, components.py, sample_data.py
│   └── views/
│       ├── resume_analysis.py     # Page 1
│       ├── job_match.py           # Page 2
│       ├── cv_improvement.py      # Page 3
│       ├── mentor.py              # Page 4
│       ├── data_index.py          # hidden dev page
│       └── evaluation.py          # hidden dev page
│
├── scripts/
│   ├── build_index.py             # rebuild the FAISS index from the job CSV
│   ├── sample_dataset.py
│   └── verify_deployment.py
│
├── tests/
│   └── test_core.py
│
├── docs/
│   └── api-provider-research.md
│
└── reports/
    ├── final_report.pdf
    ├── answer_quality.md
    └── Gen_AI_project_report.pdf
```

</details>

---

## Getting Started

**Prerequisites:** Python 3.11, and a Google Gemini API key (generation, parsing, and embeddings).

```bash
git clone https://github.com/H4r5ha/smarthire-genai.git
cd smarthire-genai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

## Configuration

Copy the environment template and add your API key:

```bash
cp .env.example .env
```

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | **Required.** Powers resume parsing, CV improvement, the mentor, and embeddings. | — |
| `GEMINI_MODEL` | Gemini model used for generation. | `gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODELS` | Comma-separated fallback models on temporary high-demand errors. | `gemini-3.7-flash,gemini-3.6-flash` |
| `EMBEDDING_PROVIDER` | `gemini-api`, `local-lsa` (offline), or `fastembed` (local neural). | `gemini-api` |
| `GEMINI_EMBEDDING_MODEL` | Dedicated Gemini embedding model. | `gemini-embedding-2` |
| `GEMINI_EMBEDDING_DIMENSION` | Embedding vector size. | `768` |
| `EMBEDDING_BATCH_SIZE` | Max texts sent to the embedding API per call. | `64` |
| `TOP_K_JOBS` | Number of job matches returned. | `8` |
| `TOP_K_MENTOR` | Number of retrieved chunks passed to the mentor prompt. | `5` |
| `MENTOR_MIN_SCORE` | Evidence relevance gate threshold for the mentor. | `0.28` |

On Streamlit Community Cloud, the same values go under **App settings → Secrets** (see `.streamlit/secrets.toml.example`) and are picked up automatically.

---

## Running the App

```bash
streamlit run streamlit_app/app.py
```

On first run, the app embeds the job corpus and builds the FAISS index automatically (this may take a moment). The sidebar will show the index as **"Ready"** once done. Rebuild it manually anytime with:

```bash
python scripts/build_index.py
```

---

## Evaluation

A developer-only **Evaluation** page and `src/evaluate.py` module cover:

- **Retrieval relevance** — Top-1 / Top-5 hit-rate benchmarking.
- **Answer quality** — correctness, grounding, and helpfulness scoring for mentor responses.
- **Prompt comparison** — before/after results from a prompt change.
- **Hallucination check** — confirms the mentor declines when evidence is insufficient.

Full results are in `reports/answer_quality.md` and `reports/final_report.pdf`.

---

## Guardrails & Safety

- A pre-LLM **keyword blocklist** plus **prompt-injection detection**, run at every LLM call site.
- The **resume text itself** is guardrail-checked before it reaches any LLM — not just chat input.
- The mentor is scoped at the **prompt level** to decline off-topic questions and admit when evidence is insufficient.
- Unhandled errors are caught globally; only server logs see the real traceback.

---

## Deployment

Deployed on **Streamlit Community Cloud:**
**[smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app](https://smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app/)**

`data/jobs/` is the source of truth; `vectorstore/` is a derived cache that rebuilds automatically if missing or stale — deployment never depends on an index built locally.

---

## Limitations

- No live scraping of LinkedIn/Naukri — matching runs against a pre-collected, embedded dataset.
- Structured parsing uses temperature 0, so re-uploading the same resume gives consistent results.
- `EMBEDDING_PROVIDER=fastembed` is a heavier local backend — use with caution on resource-constrained deployments.
