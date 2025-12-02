from unittest.mock import Mock
from datetime import datetime
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent007",
             "email": "agent007@gmail.com", "password": "12345678", "avatar": "https://twitter.com/gravatar", }


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)

    response = client.post("api/auth/register", json=user_data)

    assert response.status_code == 201, response.text
    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
