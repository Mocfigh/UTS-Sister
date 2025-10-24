# tests/test_api.py
import pytest
from httpx import AsyncClient
from src.models import Event
from src.main import create_app

@pytest.mark.asyncio
async def test_publish_single_event():
    # ✅ Pakai in-memory DB untuk test
    app = create_app(db_path=None)  # None = in-memory only
    async with AsyncClient(app=app, base_url="http://test") as client:
        event = Event(
            topic="test",
            event_id="evt-1",
            timestamp="2025-10-23T19:00:00Z",
            source="pytest",
            payload={"msg": "hello"}
        )
        response = await client.post("/publish", json=event.model_dump())
        assert response.status_code == 200
        data = response.json()
        assert data["processed"] == 1
        assert data["duplicates"] == 0
        assert data["received"] == 1

@pytest.mark.asyncio
async def test_publish_duplicate_event():
    # ✅ Pakai in-memory DB untuk test
    app = create_app(db_path=None)  # None = in-memory only
    async with AsyncClient(app=app, base_url="http://test") as client:
        event = Event(
            topic="test",
            event_id="evt-dup",
            timestamp="2025-10-23T19:05:00Z",
            source="pytest",
            payload={"msg": "duplicate"}
        )

        # Publish pertama → processed
        r1 = await client.post("/publish", json=event.model_dump())
        data1 = r1.json()
        assert r1.status_code == 200
        assert data1["processed"] == 1
        assert data1["duplicates"] == 0

        # Publish kedua → duplicate
        r2 = await client.post("/publish", json=event.model_dump())
        data2 = r2.json()
        assert r2.status_code == 200
        assert data2["processed"] == 0
        assert data2["duplicates"] == 1