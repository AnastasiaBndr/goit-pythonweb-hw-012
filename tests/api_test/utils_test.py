import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from src.database.db import get_db
from main import app


@pytest.mark.asyncio
async def test_contactbook_success(client, db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    response = client.get("/api/contactbook")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to FastAPI!"

    app.dependency_overrides.pop(get_db)

@pytest.mark.asyncio
async def test_contactbook_db_error(client):
    async def fake_get_db():
        class FakeSession:
            async def execute(self, *args, **kwargs):
                raise Exception("DB error")
        yield FakeSession()

    app.dependency_overrides[get_db] = fake_get_db

    response = client.get("/api/contactbook")
    assert response.status_code == 500
    assert response.json()["detail"] == "Error connecting to the database"

    app.dependency_overrides.pop(get_db)
