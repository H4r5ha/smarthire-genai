# API provider decision - researched 2026-09-04

## Decision

**Use Google Gemini API directly for the LLM layer.** The starter app is configured for `gemini-3.8-flash` and keeps the key in `.env` locally or Streamlit Secrets in deployment.

Why this is the best fit for this capstone:

1. The project brief explicitly permits Gemini and asks for an LLM API, structured output, RAG, guardrails and Streamlit deployment.
2. Google currently provides a free developer tier with free input/output tokens for eligible models. This is not unlimited: Gemini documents rate limits in RPM, input TPM and RPD, and limits are applied per project. See the official pricing and rate-limit pages.
3. Gemini supports structured JSON output and direct document/PDF handling, which fits resume parsing. The project itself still extracts PDF/DOCX text locally to keep the pipeline deterministic and light.
4. Gemini's current API is officially accessible from Python and also offers OpenAI compatibility, but this project uses the official Google SDK so there is one fewer routing layer.

## Important correction to the "Gemini has no limits" assumption

Gemini **does have limits**. The official rate-limit documentation explicitly describes RPM, input TPM and RPD limits and says exceeding a limit returns a rate-limit error. Free-tier limits depend on the model/project and can change, so this repository deliberately does not hard-code a numeric quota. The code uses small prompts, caches the local job vectors and only calls the LLM for resume parsing, CV improvement and mentor generation.

## Alternatives reviewed

### Groq
Very attractive for speed and has a free plan, but its API documents explicit RPM/RPD/TPM/TPD limits. For this capstone, Gemini's current free developer offering and direct structured-output/document support make the overall integration simpler.

### OpenRouter
Excellent as a multi-model gateway, but its free plan currently lists a **50 requests/day** rate limit. That is a poor fit for a public demo where students may reload the app or multiple users may test the mentor.

### xKiro
Technically capable and useful as a routing gateway: it exposes OpenAI- and Anthropic-compatible endpoints and automatic fallback. However, it adds an extra provider dependency and its available model catalog/pricing can change. It is better treated as an optional future provider than the default for this project.

### ZenMux / TeamoRouter
Both expose routing/subscription-style infrastructure. The official documentation confirms plan-based limits/usage handling, but neither provides a clearly superior fit for this small academic Streamlit deployment compared with going directly to Gemini.

### Lumosel
I did not find sufficiently authoritative current API documentation to justify making it the default dependency for an academic project that needs reproducible deployment instructions.

## Embeddings decision

The default starter configuration uses **local TF-IDF + TruncatedSVD (LSA)** to create compact dense vectors. This was chosen specifically for the user's Windows + 8 GB RAM development environment: it requires no neural-model download and avoids the CPU/RAM spike that can occur when an ONNX-based embedding model is downloaded and initialized.

The resulting dense vectors are normalized and used with cosine similarity. When `faiss-cpu` is available (for example on Linux/Streamlit Community Cloud), the vectors are stored/queryable through FAISS; on Windows the project uses an exact NumPy cosine-search fallback. An optional FastEmbed backend remains in the code but is not installed by default and should not be enabled for the first run on an 8 GB machine.

## Operational rule

Never place an API key in Python source, React/TypeScript source, CSVs, notebooks, screenshots or Git history. Local development uses `.env`; Streamlit Community Cloud uses Secrets.
