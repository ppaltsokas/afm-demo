from fastapi.testclient import TestClient
from app.main import app
from app import rag

client = TestClient(app)

class FakeModel:
    def encode(self, texts, convert_to_numpy=True):
        # deterministic tiny vectors: length of string and number of spaces
        import numpy as np
        vecs = []
        for t in texts:
            vecs.append([len(t), t.count(" ") + 1, 1.0])
        arr = np.array(vecs, dtype=float)
        # normalize like real pipeline
        n = (arr ** 2).sum(axis=1, keepdims=True) ** 0.5 + 1e-12
        return arr / n

def test_ingest_and_answer(monkeypatch):
    # Prevent real model download
    monkeypatch.setattr(rag, "get_model", lambda name="x": FakeModel())

    # Start from a clean slate
    rag.reset_index()

    # Ingest 2 docs
    payload = [
        {"id": "p1", "text": "alpha beta"},
        {"id": "p2", "text": "gamma delta epsilon"},
    ]
    r = client.post("/ingest", json=payload)
    assert r.status_code == 200
    assert r.json()["ingested"] == 2

    # Ask a question
    r2 = client.post("/answer", json={"question": "delta?"})
    assert r2.status_code == 200
    body = r2.json()
    assert "answer" in body
    assert "RAG v1" in body["answer"] or "stub" in body["answer"]
