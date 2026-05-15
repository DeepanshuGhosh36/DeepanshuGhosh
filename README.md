# SHL Conversational Recommendation Agent

Production-ready stateless FastAPI service for SHL assessment recommendation, clarification, refinement, comparison, and refusal handling.

## Architecture
- **FastAPI** API layer (`/health`, `/chat`)
- **Stateless conversation engine** that reconstructs state from full `messages`
- **Retriever** using local JSON + FAISS artifacts loaded once at startup
- **Gemini (free tier)** for response phrasing only
- **LangChain** lightweight prompt->LLM composition
- **Pydantic** strict request/response validation

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional for offline embedding generation + tests
pip install -r requirements-offline.txt
cp .env.example .env
```

## Scraper usage (manual only)
```bash
python -m app.services.scraper
```
Saves normalized catalog to `app/data/catalog.json`. Never runs at API startup.

## Embedding generation (offline only)
```bash
python -m app.services.embedder
```
Outputs:
- `app/data/embeddings.npy`
- `app/data/faiss.index`

## Run locally
```bash
uvicorn app.main:app --reload
```
Swagger: `http://localhost:8000/docs`

## Postman test
POST `/chat`
```json
{
  "messages": [
    {"role": "user", "content": "Hiring a Java developer with stakeholder interaction"}
  ]
}
```

## Railway deployment
- Uses `Dockerfile`, `railway.json`, `runtime.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment variables
- `GEMINI_API_KEY` (required for Gemini phrasing)
- `LOG_LEVEL` (optional)

## Evaluator compatibility
- Stateless: no server-side session memory
- Always-valid chat schema
- Recommendations are `[]` for clarification/refusal
- Recommendations capped at 10
- Broad exception fallback for crash-proof response envelope
