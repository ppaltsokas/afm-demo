from datetime import datetime

from .config import settings


def generate_answer(question: str) -> dict:
    # Placeholder for RAG/agent logic. Swap this with retriever + generator + guardrails.
    return {
        "answer": f"[stub:{settings.MODEL_NAME}] You asked: {question}",
        "model": settings.MODEL_NAME,
        "prompt_version": "v1.1",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "env": settings.APP_ENV,
    }
