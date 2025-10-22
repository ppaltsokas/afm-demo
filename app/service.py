from __future__ import annotations

import re
from typing import Any

import requests
from bs4 import BeautifulSoup

from . import rag
from .config import settings


def generate_answer(question: str) -> dict[str, Any]:
    try:
        hits = rag.retrieve(question, top_k=1)
        if hits:
            score, doc = hits[0]
            answer = (
                f"[RAG v1 | {settings.model}] "
                f"score={score:.3f} • context={doc.get('id','')} :: {doc.get('text','')}"
            )
        else:
            answer = f"[stub:{settings.model}] No context yet. You asked: {question}"
        return {
            "answer": answer,
            "model": settings.model,
            "prompt_version": "v1-rag",
            "timestamp": settings.now_iso(),
            "env": settings.app_env,
        }
    except Exception as e:
        return {
            "answer": f"[error] {type(e).__name__}: {e}",
            "model": settings.model,
            "prompt_version": "v1-rag",
            "timestamp": settings.now_iso(),
            "env": settings.app_env,
        }

def ingest_docs(items: list[dict[str, str]]) -> dict[str, Any]:
    try:
        n = rag.ingest(items)
        return {"ingested": n, "total_hint": "In-memory only unless /save is called."}
    except Exception as e:
        return {"ingested": 0, "error": f"{type(e).__name__}: {e}"}

def save_index() -> dict[str, Any]:
    return rag.save_index()

def load_index() -> dict[str, Any]:
    return rag.load_index()

def reset_index() -> dict[str, Any]:
    return rag.reset_index()

def _clean_text(s: str) -> str:
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def _chunk(text: str, chunk_size: int = 400, overlap: int = 40) -> list[dict]:
    # naive character chunking; good enough for v1
    chunks = []
    start = 0
    n = len(text)
    idx = 1
    while start < n:
        end = min(n, start + chunk_size)
        part = text[start:end]
        if part.strip():
            chunks.append({"id": f"u{idx}", "text": part})
            idx += 1
        if end == n:
            break
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def ingest_from_url(url: str, id_prefix: str | None = None) -> dict:
    """Fetch a page, extract visible text, chunk, and ingest."""
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # strip scripts/styles, then get text
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text(separator=" ")
    text = _clean_text(text)

    docs = _chunk(text)
    # prefix ids so multiple URLs don't collide
    prefix = (id_prefix or re.sub(r'[^a-zA-Z0-9]+', '-', url)).strip("-")
    for d in docs:
        d["id"] = f"{prefix}-{d['id']}"
        d["meta"] = {"source_url": url}

    n = rag.ingest(docs)
    return {"ingested": n, "chunks": len(docs)}