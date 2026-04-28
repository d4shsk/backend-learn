import pytest
from httpx import AsyncClient, ASGITransport

from main import app

# интеграционные тесты для main.py

@pytest.mark.asyncio
async def test_get_books():
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        responce = await client.get("/books")
        assert responce.status_code == 200

        data = responce.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_book():
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as client:
        responce = await client.post("/books", json={"title": "new book"})

        assert responce.status_code == 200

        data = responce.json()
        assert data["title"] == "new book"
