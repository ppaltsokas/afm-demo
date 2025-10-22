from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

# ---------- Globals (in-memory index) ----------
_model: SentenceTransformer | None = None
_corpus: list[dict[str, str]] = []          # [{id:str, text:str, meta?:dict}]
_matrix: np.ndarray | None = None         # (N, D) normalized embeddings

# ---------- Storage paths ----------
DATA_DIR = Path("data")
CORPUS_PATH = DATA_DIR / "corpus.jsonl"
EMB_PATH = DATA_DIR / "embeddings.npy"

# ---------- Model ----------
def get_model(name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(name)
    return _model

# ---------- Helpers ----------
def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / n

def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Core API ----------
def ingest(documents: list[dict[str, str]]) -> int:
    """
    documents: list of dicts with {"id": str, "text": str, ...}
    Returns number ingested.
    """
    global _corpus, _matrix
    if not documents:
        return 0
    model = get_model()
    texts = [d["text"] for d in documents]
    emb = model.encode(texts, convert_to_numpy=True)
    emb = _normalize(emb)
    _corpus.extend(documents)
    _matrix = emb if _matrix is None else np.vstack([_matrix, emb])
    return len(documents)

def retrieve(query: str, top_k: int = 3) -> list[tuple[float, dict[str, str]]]:
    global _corpus, _matrix
    if not _corpus or _matrix is None:
        return []
    model = get_model()
    q = model.encode([query], convert_to_numpy=True)
    q = _normalize(q)[0]  # (D,)
    # cosine = dot since normalized
    scores = _matrix @ q  # (N,)
    idx = np.argsort(-scores)[:top_k]
    return [(float(scores[i]), _corpus[i]) for i in idx]

# ---------- Persistence ----------
def save_index() -> dict[str, str]:
    """Save corpus and embeddings to disk."""
    global _corpus, _matrix
    _ensure_data_dir()

    # Save corpus (JSONL)
    with CORPUS_PATH.open("w", encoding="utf-8") as f:
        for d in _corpus:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    # Save embeddings (npy)
    if _matrix is not None:
        np.save(EMB_PATH, _matrix)
    else:
        # If empty, ensure no stale file remains
        if EMB_PATH.exists():
            EMB_PATH.unlink()

    return {"saved": "ok", "path": str(DATA_DIR)}

def load_index() -> dict[str, str]:
    """Load corpus and embeddings from disk, if present."""
    global _corpus, _matrix
    if not CORPUS_PATH.exists() or not EMB_PATH.exists():
        return {"loaded": "empty"}

    # Load corpus
    corpus: list[dict[str, str]] = []
    with CORPUS_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                corpus.append(json.loads(line))

    # Load embeddings
    emb = np.load(EMB_PATH)
    # Basic integrity check
    if len(corpus) != emb.shape[0]:
        raise ValueError("Corpus/embedding size mismatch")

    _corpus = corpus
    _matrix = emb
    return {"loaded": "ok", "count": str(len(_corpus))}

def reset_index() -> dict[str, str]:
    """Clear memory and remove on-disk files."""
    global _corpus, _matrix
    _corpus = []
    _matrix = None
    # Clean files
    if CORPUS_PATH.exists():
        CORPUS_PATH.unlink()
    if EMB_PATH.exists():
        EMB_PATH.unlink()
    return {"reset": "ok"}
