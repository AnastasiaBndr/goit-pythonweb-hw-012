from unittest.mock import patch
from src.schemas import UserRole
from conftest import test_user,auth_service
from src.database.models import User
from src.security.hashing import Hash
import pytest

def test_get_me(client, get_token):
    response = client.get(
        "api/users/me", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]


@patch("src.services.upload_file.UploadFileService.upload_file")
def test_update_avatar_user(mock_upload_file, client, get_token):
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url

    headers = {"Authorization": f"Bearer {get_token}"}

    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar",
                            headers=headers, files=file_data)

    assert response.status_code == 200, response.text

    data = response.json()
    print(data)
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["avatar"] == fake_url

    mock_upload_file.assert_called_once()


def test_public(client, get_token):
    response = client.get(
        "api/users/public", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Public!"


def test_public_admin(client, get_token):
    response = client.get(
        "api/users/admin", headers={"Authorization": f"Bearer {get_token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == f"Greetings, {test_user["username"]}! This is admin route"


@pytest.mark.asyncio
async def test_admin_route_forbidden(client, db_session):
    user = User(
        username="simple_user",
        email="simple@example.com",
        hashed_password=Hash().get_password_hash("12345678"),
        avatar="twitter.com",
        user_role=UserRole.USER,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    token = await auth_service.create_access_token(data={"sub": user.username})

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("api/users/admin", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == "No access rights"
