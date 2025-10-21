
# AFM Demo – FastAPI + Docker + CI (RAG-ready scaffold)

A minimal, production-ready scaffold to demo a small GenAI/RAG/agent service:

- **FastAPI** app with health, versioned prompts, and a stub `/answer` endpoint.
- **Tests** with `pytest`.
- **CI** via GitHub Actions (lint + tests).
- **Docker** for containerized deploys.
- **Makefile** for common tasks.
- **Config** with Pydantic settings.

## Local dev

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
make run                                            # http://localhost:8000/healthz
make test
```

## Docker build & run

```bash
docker build -t afm-demo:latest .
docker run -p 8000:8000 --env-file .env afm-demo:latest
```

## Deploy (Render or Cloud Run)

### Option A: Google Cloud Run
1. `gcloud auth login` and `gcloud config set project <PROJECT_ID>`
2. Build & push:
   ```bash
   gcloud builds submit --tag gcr.io/<PROJECT_ID>/afm-demo:latest
   ```
3. Deploy:
   ```bash
   gcloud run deploy afm-demo \
     --image gcr.io/<PROJECT_ID>/afm-demo:latest \
     --platform managed \
     --region europe-west1 \
     --allow-unauthenticated \
     --set-env-vars APP_ENV=prod
   ```

### Option B: Render
- Connect the repo, choose **Docker**.
- Set environment var `APP_ENV=prod`.
- Auto-deploy on push.

## Endpoints

- `GET /healthz` → liveness
- `POST /answer` → stubbed RAG/agent answer with prompt version tagging

## Configuration

Environment variables (via `.env` or platform secrets):

- `APP_ENV` – `dev` or `prod` (default: `dev`)
- `MODEL_NAME` – logical model name label (default: `mock-001`)

## Extending to RAG

- Add a `/ingest` endpoint to index documents (FAISS/pgvector).
- Implement chunking (200–500 tokens), embeddings, and retrieval (BM25/dense).
- Add an evaluation script in `eval/` to score a tiny QA set.

## Project layout

```
.
├── app/
│   ├── main.py
│   ├── config.py
│   └── service.py
├── tests/
│   └── test_app.py
├── .github/workflows/ci.yml
├── .gitignore
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```
