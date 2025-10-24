import pytest
from httpx import AsyncClient
from src.main import create_app

@pytest.fixture
async def app():
    """FastAPI app in-memory"""
    app_instance = create_app(db_path=None)
    # Start EventProcessor
    await app_instance.state.event_processor.start()
    yield app_instance
    await app_instance.state.event_processor.stop()

@pytest.fixture
async def client(app):
    """
    Async HTTP client untuk test endpoint
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac  # pastikan yield AsyncClient instance
