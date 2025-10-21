# AFM Demo — FastAPI · Docker · CI (RAG-ready)

Minimal service scaffold for GenAI/RAG/agent experiments. Runs locally, in Docker, and on Cloud Run. CI runs lint + tests on every push.

## What’s inside
- FastAPI app with `/healthz` and a stubbed `/answer`
- Config via Pydantic (env-driven)
- Tests with `pytest` (async client)
- Ruff for linting
- Dockerfile (small, Python 3.11 slim)
- GitHub Actions workflow (lint + tests)

---

## Quick start (local)

```bash
# create venv
python -m venv .venv
# activate
#  - Windows PowerShell:
.\.venv\Scriptsctivate
#  - macOS/Linux:
# source .venv/bin/activate

# install deps
pip install -r requirements.txt

# run dev server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# open: http://localhost:8000/healthz and http://localhost:8000/docs
```

### Tests & lint
```bash
pytest -q
ruff check .
ruff check --fix .   # auto-fix import order, etc.
```

---

## Configuration

Create `.env` (copy from `.env.example`):

```
APP_ENV=dev
MODEL_NAME=mock-001
```

These show up in `/answer` responses so you can verify which env/model is active.  
Change `.env`, restart the app (or pass envs at container runtime).

---

## Docker

```bash
# build image
docker build -t afm-demo:latest .

# run with env file
docker run -p 8000:8000 --env-file .env afm-demo:latest

# open:
#   http://localhost:8000/healthz
#   http://localhost:8000/docs
```

`.dockerignore` excludes venv, caches, and `.env` so secrets don’t get baked into images.

---

## Deploy — Google Cloud Run (Milan / europe-west8)

Prereqs: Google Cloud SDK installed, a GCP project with Billing, and required APIs enabled:
```bash
gcloud auth login
gcloud config set project <PROJECT_ID>
gcloud config set run/region europe-west8
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Build + push to **Artifact Registry** (creates the repo once):
```bash
gcloud artifacts repositories create afm-repo   --repository-format=docker   --location=europe-west8   --description="afm images" || true
```

Build and tag by commit (from the project folder with the Dockerfile):
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
  --set-env-vars APP_ENV=prod,MODEL_NAME=demo-xyz
```

Get URL:
```bash
gcloud run services describe afm-demo --region europe-west8 --format="value(status.url)"
```

### Logs
```bash
# one-shot
gcloud run services logs read afm-demo --region europe-west8 --limit 50

# live tail (needs beta component)
gcloud beta run services logs tail afm-demo --region europe-west8
```

### Update env vars (no rebuild)
```bash
gcloud run services update afm-demo --region europe-west8 `
  --update-env-vars APP_ENV=prod,MODEL_NAME=demo-xyz-2
```

### Reasonable runtime limits
```bash
gcloud run services update afm-demo --region europe-west8 --max-instances 3
gcloud run services update afm-demo --region europe-west8 --cpu 1 --memory 512Mi --concurrency 80 --timeout 60
```

---

## Endpoints

- `GET /healthz` — liveness
- `POST /answer` — stub answer with prompt/version + env/model echo  
  Example:
  ```json
  { "question": "What is this service?" }
  ```

---

## Project layout

```
.
├── app/
│   ├── main.py         # FastAPI routes
│   ├── service.py      # business logic (stub now; drop RAG/agent here)
│   └── config.py       # env-driven settings
├── tests/
│   └── test_app.py     # health + answer tests (async httpx client)
├── .github/workflows/ci.yml
├── .dockerignore
├── .gitignore
├── Dockerfile
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```



