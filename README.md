# AFM Demo — FastAPI · Docker · CI (RAG v1)
![CI](https://github.com/ppaltsokas/afm-demo/actions/workflows/ci.yml/badge.svg)

Minimal, production-style FastAPI service with a tiny **RAG v1**:
- Sentence-Transformers embeddings (MiniLM) + cosine similarity (NumPy)
- In-memory index with **/save**, **/load**, **/reset** persistence to `data/`
- **/ingest_url** to fetch & chunk a web page (e.g., GitHub README)
- Clean config via Pydantic Settings (`.env`)
- Tests (pytest + TestClient) with a **fake embedding model** for speed
- Dockerfile + GitHub Actions (lint + tests on every push)

> The first call to `/ingest` or `/ingest_url` loads the embedding model and can take a few seconds.

---

## What’s inside
- `app/main.py` — routes (health, RAG endpoints, error handler, lifespan auto-load)
- `app/service.py` — business logic (RAG wrapper + persistence)
- `app/rag.py` — embedding model, ingestion, retrieval, save/load/reset
- `tests/test_rag.py` — fast unit test (no model download)
- CI: `.github/workflows/ci.yml` (pip cache, ruff lint, pytest)
- Tooling: `pyproject.toml` (Ruff config), `requirements.txt`

---

## Quick start (local)

```bash
# Create venv
python -m venv .venv

# Activate
# - Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# - macOS/Linux:
# source .venv/bin/activate

# Install deps
python -m pip install -U pip
pip install -r requirements.txt

# Create env file (or copy from .env.example)
# Windows:
copy .env.example .env
# macOS/Linux:
# cp .env.example .env

# Run dev server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
# Open: http://127.0.0.1:8000/docs
```

### Tests & lint
```bash
pytest -q
ruff check .
ruff check --fix .   # auto-fix import order, minor issues
```

---

## Configuration

Create `.env` (or copy `.env.example`):
```
APP_ENV=local
MODEL_NAME=demo-xyz-2
```

These values show up in `/answer` responses (handy to verify environment/model).  
You can change them at runtime via container envs in Docker/Cloud Run.

---

## Endpoints

- `GET /healthz` — liveness
- `POST /ingest` — ingest a list of `{ id, text, meta? }`
- `POST /ingest_url` — fetch a URL, extract visible text, chunk, ingest
- `POST /answer` — retrieve best context and return a simple answer JSON
- `POST /save` — persist corpus + embeddings to `data/`
- `POST /load` — load saved index (also auto-loads on startup if present)
- `POST /reset` — clear memory and delete on-disk index
- `GET /docs` — Swagger UI

### Try it quickly (Swagger)
1. Open `http://127.0.0.1:8000/docs`
2. **POST /ingest** → “Try it out” → body:
   ```json
   [
     {"id":"p1","text":"AFM demo is a FastAPI service with Cloud Run deployment."},
     {"id":"p2","text":"Retrieval uses sentence embeddings and cosine similarity."},
     {"id":"p3","text":"Vectors are stored in memory; persistence saves to disk."}
   ]
   ```
3. **POST /answer** → body:
   ```json
   {"question":"How do you retrieve answers?"}
   ```
4. (Optional) **POST /save** (writes to `data/`), restart app, **POST /load**.

### Ingest from a URL
```
POST /ingest_url
{
  "url": "https://raw.githubusercontent.com/ppaltsokas/afm-demo/main/README.md",
  "id_prefix": "readme"
}
```

---

## Docker

```bash
# Build image
docker build -t afm-demo:latest .

# Run with env file
docker run --rm -p 8000:8000 --env-file .env afm-demo:latest

# Open:
#   http://127.0.0.1:8000/healthz
#   http://127.0.0.1:8000/docs
```

`.dockerignore` excludes venv, caches and `.env` so secrets don’t end up in images.

---

## Deploy — Google Cloud Run (example: europe-west8)

Prereqs: Google Cloud SDK, a project with Billing; enable APIs:
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud config set run/region europe-west8
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Create the Artifact Registry (once):
```bash
gcloud artifacts repositories create afm-repo \
  --repository-format=docker \
  --location=europe-west8 \
  --description="afm images" || true
```

Build & tag by commit:
```bash
# Windows PowerShell
$commit = (git rev-parse --short HEAD)
gcloud builds submit --tag europe-west8-docker.pkg.dev/<PROJECT_ID>/afm-repo/afm-demo:$commit
```

Deploy:
```bash
gcloud run deploy afm-demo `
  --image europe-west8-docker.pkg.dev/<PROJECT_ID>/afm-repo/afm-demo:$commit `
  --region europe-west8 `
  --platform managed `
  --allow-unauthenticated `
  --port 8000 `
  --set-env-vars APP_ENV=prod,MODEL_NAME=demo-xyz-2
```

Get URL:
```bash
gcloud run services describe afm-demo --region europe-west8 --format="value(status.url)"
```

Logs:
```bash
gcloud run services logs read afm-demo --region europe-west8 --limit 50
# or live tail:
gcloud beta run services logs tail afm-demo --region europe-west8
```

Reasonable runtime limits:
```bash
gcloud run services update afm-demo --region europe-west8 --max-instances 3
gcloud run services update afm-demo --region europe-west8 --cpu 1 --memory 512Mi --concurrency 80 --timeout 60
```

> Note: Local `data/` persistence is **ephemeral** in Cloud Run.  
> For production persistence, swap `rag.save_index/load_index` to Google Cloud Storage or a DB.

---

## Project layout

```
.
├── app/
│   ├── __init__.py
│   ├── config.py        # Pydantic Settings (.env)
│   ├── main.py          # FastAPI routes + lifespan + JSON error handler
│   ├── rag.py           # embeddings, ingest, retrieve, save/load/reset
│   └── service.py       # thin service layer over rag.py
├── data/                # saved corpus/embeddings (gitignored)
├── tests/
│   ├── test_app.py
│   └── test_rag.py      # uses a fake embedding model for speed
├── .github/workflows/ci.yml
├── .dockerignore
├── .gitignore
├── .env.example
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## Dependencies

Key pins/notes:
- Python 3.11
- FastAPI + Uvicorn
- Pydantic v2 (`pydantic-settings`)
- **sentence-transformers 3.x** (compatible with modern `huggingface_hub`)
- NumPy
- requests + beautifulsoup4 (for `/ingest_url`)
- pytest, ruff

```
pip install -r requirements.txt
```

---

## Roadmap
- `/answer` parameters: `top_k`, `min_score`, return matched **sources** (ids + URLs)
- Persist to Google Cloud Storage instead of local disk
- Tiny HTML UI served by FastAPI for a click-to-try demo
