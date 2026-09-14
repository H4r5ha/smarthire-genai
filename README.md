# SmartHire GenAI — Resume Matching & AI Career Mentor

An end-to-end Generative AI career portal: parse a resume, find matching jobs through semantic search, get AI-generated CV improvement suggestions, and chat with a RAG-based AI Career Mentor — all built with prompt engineering, structured output, embeddings, FAISS, LangChain, guardrails, and Streamlit.

**Live app:** https://smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app/

---

## Table of Contents

- [Overview](#overview)
- [Live Demo](#live-demo)
- [Features](#features)
  - [Page 1 — Resume Upload](#page-1--resume-upload)
  - [Page 2 — Job Match](#page-2--job-match)
  - [Page 3 — CV Improvement](#page-3--cv-improvement)
  - [Page 4 — AI Career Mentor](#page-4--ai-career-mentor)
  - [Cross-Cutting / System-Level Features](#cross-cutting--system-level-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [Evaluation](#evaluation)
- [Guardrails & Safety](#guardrails--safety)
- [Deployment](#deployment)
- [Limitations & Notes](#limitations--notes)

---

## Overview

SmartHire GenAI is a capstone Generative AI project that takes a student from **"here's my resume"** to **"here's how to land this specific job"** in a single guided flow:

1. Upload or paste a resume → get a structured, parsed profile.
2. Match against a pre-collected job corpus (or a pasted job description) → get ranked, explainable job matches.
3. Get an ATS-style before/after score, a prioritized skill gap analysis, and section-by-section rewritten resume content for a chosen target job.
4. Ask an AI Career Mentor questions about that specific resume and job — answered strictly through retrieval-augmented generation (RAG) over a job corpus and a career-notes knowledge base, with guardrails preventing off-topic or unsafe use.

In line with LinkedIn/Naukri Terms of Service, the app does **not** scrape live job boards. It uses a pre-collected job dataset that is embedded and searched semantically — the GenAI-native way of "finding related jobs."

## Live Demo

| | |
|---|---|
| **App** | https://smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app/ |
| **Source code** | https://github.com/H4r5ha/smarthire-genai |

A **Demo/Sample-data mode** toggle in the sidebar fills every page with clearly-labelled sample data end-to-end, so the full flow can be explored without uploading a real resume.

---

## Features

### Page 1 — Resume Upload

- Accepts **PDF, DOCX, and TXT** resumes, or one of the built-in sample resumes for quick testing.
- **Privacy-friendly screenshot path**: users uncomfortable uploading a full resume can instead upload up to **4 cropped screenshots** (PNG/JPG/WEBP, up to 10MB each) of just the sections they're comfortable sharing.
- Resume text is parsed by an LLM into a clean, structured JSON profile (name, skills, experience, education, target role) and validated before use.
- A **profile completeness score (0–100%)** is generated after parsing, with a checklist (Name, Contact, Target role, Skills, Experience, Education) showing exactly what's missing.
- A guardrail/safety check runs on the **extracted resume text itself**, before anything is sent downstream to the LLM — not only on later chat questions.
- Uploaded resumes are processed through a temp file that is deleted immediately after parsing; nothing persists on disk.
- Resume text is capped at a maximum character length before being sent to the LLM, protecting against oversized documents.
- A button at the bottom navigates to the Job Match page once parsing is complete.

### Page 2 — Job Match

- Users can **paste a job description**, or **search for a target role** from a dropdown of suggested roles.
- After parsing, the system automatically suggests the **top 3 roles** matching the uploaded resume; the user picks one.
- **Custom/typo-tolerant role search**: a non-catalog title like "software developer" is matched against the real job dataset by prefix, substring, and token overlap — not restricted to a fixed dropdown.
- **Two scoring modes**:
  - An exact **role search** returns only jobs from that strict role family (so a "Python Developer" search won't surface a "GCP Data Engineer" just because both mention Python).
  - A **free-text/JD search** blends semantic similarity with direct skill overlap.
- **Skill-name normalization** so equivalent variants (e.g. `React.js` / `React` / `ReactJS`, `MySQL` / `My-SQL`, `Node.js`, AWS/GCP/Azure ML variants, `C` vs `C++` vs `C#`) are treated as the same skill instead of being scored as different ones.
- **Role gating**: a job is only surfaced for a role if the candidate has the mandatory anchor skill for it (e.g. a "Data Scientist" match requires Python/ML evidence; an "AWS Data Engineer" match requires AWS specifically), preventing nonsense matches from semantic similarity alone.
- **Soft-skill filtering**: matched/missing skill chips — and the match-percentage math behind them — exclude soft/interpersonal terms like "Project Management" or "Consulting," keeping this page purely technical.
- Each match card shows a **"why" explanation string** (e.g. *"4 of 9 listed skills found on your resume; profile similarity 0.81"*) for transparency.
- The FAISS index **auto-detects a stale build** (if the underlying job CSV changed since the last build) and silently rebuilds itself, with a NumPy cosine-similarity fallback if FAISS isn't available in the runtime environment.
- Pasting a JD triggers a small LLM step that auto-extracts a clean job title from the **full pasted text** (not just the first line), with a heuristic fallback if that call fails.
- Selecting a role and hitting send automatically advances the user to the CV Improvement page.

### Page 3 — CV Improvement

- Displays **before/after ATS scores** that can never drift out of sync with what's shown on screen:
  - **Before** is computed **deterministically** from actual matched/missing skill counts (not an LLM guess).
  - **After** is a capped projection based on the real content generated on this page (rewritten bullets, summary, soft-skill additions).
- **"Missing Technical Skills" priority grouping** — skills are grouped into **High / Medium / Low** priority, each rendered as its own color-tinted, left-bordered block with a badge, an arrow, and its skill chips on one line.
- A **dedicated "soft skills the JD wants" section**, kept separate from the technical skill-gap chips (since Job Match filters soft skills out entirely).
- **Section-specific rewrites**: experience bullets, projects, certifications, and achievements each get their own rewritten version rather than one generic rewrite pass.
- Suggests a concrete set of skills to learn to close the gap and improve the ATS score.
- A button at the bottom navigates to the AI Career Mentor page.

### Page 4 — AI Career Mentor

- A **RAG chatbot** scoped strictly to questions relevant to the user's resume and the selected job description — off-topic questions are declined and redirected.
- **Role-aware, deterministic suggested questions** the user can tap instead of typing — these change with the selected target role/job but don't change randomly between reruns.
- A **TARGET JOB summary card** (role, company, location, "Change Job" button) — the same component used on the CV Improvement page — stays visible while chatting so the active role/job context is never lost.
- **RAG pipeline staged as 5 explicit steps** — Guardrail → Retrieve → Prompt → Gemini → Output — built as a real LangChain LCEL chain.
- **Blended retrieval** from two knowledge sources: the job postings corpus and a separate career-notes knowledge base (role roadmaps/guides), combined with a lexical-overlap boost on top of embedding similarity.
- **Evidence relevance gate**: if the best retrieved evidence scores below a confidence threshold, the mentor explicitly says it doesn't have enough evidence rather than guessing.
- **Answer-completeness self-check**: if a generated answer looks truncated or cut off mid-sentence, the pipeline automatically retries generation once with a corrective prompt before returning it to the user.
- **Natural, non-templated answers**: no rigid "80–140 words, max 4 bullets" formatting rule and no forced numbered-section structure — the mentor matches its structure to the question's actual complexity, defaulting to plain prose/bullets and staying within a soft ~250-word guideline (with an explicit exception for genuinely multi-part questions).
- **Layered scope guardrail**: a pre-LLM keyword blocklist plus an explicit prompt-level instruction to decline and redirect any question outside career/resume/job-search topics.
- Sources shown to the user include a **relevance score per source**, and every answer carries a **pipeline trace** (which stages ran) for transparency and debugging.

### Cross-Cutting / System-Level Features

- **Demo/Sample-data mode** — a sidebar toggle that fills every page with clearly-labelled sample data end-to-end, for testing without uploading a real resume.
- **Persistent sidebar status panel** — live indicators for whether the vector index is "Ready" and whether the mentor RAG is "Online/Offline," plus the current candidate's name, target role, and skill count.
- **Two developer-only pages** exist in the codebase but are hidden from the main navigation:
  - **Data & Index Management** — dataset stats, rebuild-index / refresh-data actions, pipeline visualization.
  - **Evaluation dashboard** — retrieval Top-1/Top-5 hit-rate benchmarking, addressing the project's required evaluation section.
- **Global error handling** — any unhandled page error is caught and shown to the user as a friendly message; the real traceback is only written to server logs, never exposed in the UI.
- **Prompt-injection guardrails** — patterns such as "ignore previous instructions," "reveal system prompt," and "jailbreak" are blocked in addition to the off-topic keyword blocklist, on **every** LLM call site (resume parsing, CV generation, JD title extraction, mentor chat) — not just the chatbot.
- Automatic background **embedding/indexing on first run** — no manual setup step required; the app builds its FAISS index on startup if one doesn't already exist (initial startup may take a little longer while this happens).

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM & embeddings | Google Gemini (generation + embedding models), configurable via `.env` |
| Orchestration | LangChain (LCEL chain for the mentor RAG pipeline) |
| Vector store | FAISS (with a NumPy cosine-similarity fallback) |
| Document parsing | `pypdf`, `python-docx` |
| Data handling | `pandas`, `numpy`, `scikit-learn` |
| UI | Streamlit |
| Deployment | Streamlit Community Cloud |

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
        ├──► embed profile ──► FAISS search ──► top-N matching jobs (role-gated, skill-normalized)
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

## Project Structure

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

## Getting Started

### Prerequisites

- Python **3.11**
- A Google **Gemini API key** (for generation, structured parsing, and embeddings)

### Installation

```bash
git clone https://github.com/H4r5ha/smarthire-genai.git
cd smarthire-genai

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Copy the environment template and add your API key:

```bash
cp .env.example .env
```

Key variables in `.env`:

| Variable | Purpose | Default |
|---|---|---|
| `GEMINI_API_KEY` | **Required.** Enables live resume parsing, CV improvement, the grounded mentor, and Gemini-based embeddings. | — |
| `GEMINI_MODEL` | Gemini model used for generation. | `gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODELS` | Comma-separated fallback models used on temporary availability/high-demand errors. | `gemini-3.7-flash,gemini-3.6-flash` |
| `EMBEDDING_PROVIDER` | `gemini-api` (cloud), `local-lsa` (offline TF-IDF + TruncatedSVD), or `fastembed` (optional local neural backend). | `gemini-api` |
| `GEMINI_EMBEDDING_MODEL` | Dedicated Gemini embedding model. | `gemini-embedding-2` |
| `GEMINI_EMBEDDING_DIMENSION` | Embedding vector size. | `768` |
| `EMBEDDING_BATCH_SIZE` | Max texts sent to the embedding API/model per call. | `64` |
| `TOP_K_JOBS` | Number of job matches returned. | `8` |
| `TOP_K_MENTOR` | Number of retrieved chunks passed to the mentor prompt. | `5` |
| `MENTOR_MIN_SCORE` | Evidence relevance gate threshold for the mentor. | `0.28` |

When deploying on Streamlit Community Cloud, the same values are configured via **App settings → Secrets** using the format in `.streamlit/secrets.toml.example`, and are picked up automatically — no code changes required.

## Running the App

```bash
streamlit run streamlit_app/app.py
```

On first run, the app automatically embeds the job corpus and builds the FAISS index if one isn't already present — this can take a little while, after which the sidebar status panel will show the index as **"Ready."** The index can also be rebuilt manually:

```bash
python scripts/build_index.py
```

## Evaluation

The project includes a dedicated (developer-only) **Evaluation** page and a `src/evaluate.py` module covering:

- **Retrieval relevance** — Top-1/Top-5 hit-rate benchmarking for sample profiles.
- **Answer quality** — correctness, grounding, and helpfulness scoring for mentor responses.
- **Prompt comparison** — a before/after comparison showing how a prompt change improved output.
- **Hallucination check** — confirms the mentor correctly declines or says it lacks sufficient evidence when the answer isn't in the retrieved documents.

Results are written up in `reports/answer_quality.md` and `reports/final_report.pdf`.

## Guardrails & Safety

- A pre-LLM **keyword blocklist** plus **prompt-injection pattern detection** (e.g. "ignore previous instructions," "reveal system prompt," "jailbreak") run at every LLM call site — resume parsing, CV generation, JD title extraction, and mentor chat.
- The extracted **resume text itself** is guardrail-checked before it's ever sent to an LLM, not only chat input.
- The mentor is additionally scoped at the **prompt level** to decline and redirect any question outside career/resume/job-search topics, and will explicitly state when it lacks enough retrieved evidence rather than answering ungrounded.
- Any unhandled application error is caught globally and shown as a friendly message, with the full traceback routed only to server logs.

## Deployment

The app is deployed on **Streamlit Community Cloud**:

**https://smarthire-genaigit-ecdmnsbsbnk9qckhqnbubk.streamlit.app/**

The job CSV in `data/jobs/` is the deployable source of truth; the FAISS index in `vectorstore/` is a derived cache that is rebuilt automatically on startup if it's missing or stale, so deployment does not depend on an index built on a developer machine.

## Limitations & Notes

- No live scraping of LinkedIn/Naukri is performed, in line with each platform's Terms of Service — job matching runs against a pre-collected, embedded dataset instead.
- Structured resume parsing uses a fixed decoding seed with temperature 0, so re-uploading the identical resume/screenshot consistently extracts the same skills/target role.
- `EMBEDDING_PROVIDER=fastembed` is a heavier, local neural backend intended for notebook comparisons — use with caution if deployed to a resource-constrained environment.
