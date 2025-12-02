import pytest
from unittest.mock import AsyncMock, patch
from src.services.users import UserService
from src.schemas import UserCreate


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def user_service(mock_repo):
    with patch("src.services.users.UsersRepository", return_value=mock_repo):
        service = UserService(db=None)
        yield service


@pytest.mark.asyncio
async def test_register_user_success(user_service, mock_repo):
    mock_repo.get_user_by_username.return_value = None
    mock_repo.create_user.return_value = {"username": "testuser"}

    user_create = UserCreate(
        username="testuser", email="test@test.com", password="password")
    result = await user_service.register_user(user_create)

    assert result["username"] == "testuser"
    mock_repo.get_user_by_username.assert_awaited_once_with("testuser")
    mock_repo.create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_exists(user_service, mock_repo):
    mock_repo.get_user_by_username.return_value = {"username": "existing"}
    user_create = UserCreate(
        username="existing", email="existing@test.com", password="password")

    result = await user_service.register_user(user_create)
    assert result is None
    mock_repo.create_user.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_user_by_email(user_service, mock_repo):
    mock_repo.get_user_by_email.return_value = {"email": "test@test.com"}

    result = await user_service.get_user_by_email("test@test.com")
    assert result["email"] == "test@test.com"
    mock_repo.get_user_by_email.assert_awaited_once_with("test@test.com")


@pytest.mark.asyncio
async def test_reset_password(user_service, mock_repo):
    mock_repo.reset_password.return_value = True

    result = await user_service.reset_password("test@test.com", "newpass")
    assert result is True
    mock_repo.reset_password.assert_awaited_once()
