import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_healthz():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.get("/healthz")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_answer():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/answer", json={"question": "Hello?"})
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert "answer" in data and "stub" in data["answer"]
