
from fastapi import FastAPI
from pydantic import BaseModel
from .service import generate_answer

app = FastAPI(title="AFM Demo", version="0.1.0")

class Question(BaseModel):
    question: str

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/answer")
def answer(payload: Question):
    return generate_answer(payload.question)
