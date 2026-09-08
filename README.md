# SmartHire GenAI - Resume Matching & AI Career Mentor

A deployable Streamlit implementation of the SmartHire capstone described in the supplied project brief. The provided UI package has been connected to a real Python backend while preserving the supplied visual structure and navigation.

## What is implemented

- Resume parser: PDF/DOCX/TXT extraction -> Gemini structured JSON profile.

- Semantic job search: 80 cleaned Naukri postings -> dense embeddings -> FAISS/NumPy cosine retrieval.

- CV improvement: Gemini-generated skill gaps, summary rewrite, bullet improvements and recommendations for a selected job.

- AI Career Mentor: guardrails -> retrieval from job corpus + career notes -> evidence gate -> Gemini response with source labels.

- Data & Index page: real dataset/index status and rebuild action.

- Evaluation page: small starter retrieval benchmark; human mentor scoring remains a final-report task.

- Deployment target: Streamlit Community Cloud.

The project brief identifies the core passing scope as a working Streamlit app with resume parsing, semantic job search and mentor RAG. CV improvement and evaluation strengthen the submission.

## Important architecture choice

The final runtime UI is **Streamlit** because the project brief specifies Streamlit as the portal interface and deployment target.

The React/Vite files supplied in the UI ZIP are retained under `ui_reference/react_ui/` as the original design source. The production app is the Streamlit implementation in `streamlit_app/`, because that is the path that can be pushed directly to GitHub and deployed on Streamlit Community Cloud with Python.

## Dataset

`data/jobs/smarthire_jobs_80.csv` contains exactly 80 records. This is the dataset wired into the application and is the deployable source of truth.

The project brief specifies using a pre-collected Kaggle job dataset, embedding the job descriptions, and searching them semantically rather than performing live LinkedIn/Naukri scraping.

See `START.md` for Windows Command Prompt setup and instructions for working with the 80-row dataset.

## Deployment architecture note

The job CSV is the deployable source of truth. The vectorstore is a derived cache. On startup, the app automatically creates the index from the committed 80-job CSV when no suitable index artifact exists, so deployment does not depend on a vector index generated on the developer's Windows PC. Streamlit Community Cloud copies repository files into the deployment environment and installs the declared dependencies from `requirements.txt`.
