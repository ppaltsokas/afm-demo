# app/main.py
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel

from .service import generate_answer, ingest_docs, load_index, reset_index, save_index


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        load_index()
    except Exception:
        pass
    yield
    # Shutdown (nothing for now)

app = FastAPI(title="AFM Demo", lifespan=lifespan)

@app.exception_handler(Exception)
async def all_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=200, content={"answer": f"[error] {type(exc).__name__}: {exc}"})



@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

class Ask(BaseModel):
    question: str

@app.post("/answer")
def answer(body: Ask):
    return generate_answer(body.question)

class Doc(BaseModel):
    id: str
    text: str
    meta: dict[str, Any] | None = None

@app.post("/ingest")
def ingest(body: list[Doc]):
    return ingest_docs([d.model_dump() for d in body])


@app.post("/save")
def save():
    return save_index()

@app.post("/load")
def load():
    return load_index()

@app.post("/reset")
def reset():
    return reset_index()

class IngestURL(BaseModel):
    url: str
    id_prefix: str | None = None

@app.post("/ingest_url")
def ingest_url(body: IngestURL):
    from .service import ingest_from_url  # local import to avoid circulars at import time
    return ingest_from_url(body.url, body.id_prefix)
