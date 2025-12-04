import pytest
from tests.conftest import TestingSessionLocal
from src.repository.users import UsersRepository
from src.schemas import UserCreate
from src.security.hashing import Hash


@pytest.mark.asyncio
async def test_create_and_get_user(init_models_wrap):
    async with TestingSessionLocal() as session:
        repo = UsersRepository(session)

        user_data = UserCreate(username="spiderman",
                               email="spidey@example.com",
                               password= "12345678")
        avatar = "https://avatar.example.com/spidey.png"

        user = await repo.create_user(user_data, password=Hash().get_password_hash(user_data.password), avatar=avatar)

        assert user.id is not None
        assert user.username == "spiderman"
        assert user.email == "spidey@example.com"
        assert user.avatar == avatar

        user_by_id = await repo.get_user_by_id(user.id)
        assert user_by_id.email == "spidey@example.com"

        user_by_email = await repo.get_user_by_email("spidey@example.com")
        assert user_by_email.username == "spiderman"

        user_by_username = await repo.get_user_by_username("spiderman")
        assert user_by_username.email == "spidey@example.com"


@pytest.mark.asyncio
async def test_reset_password_and_confirm_email(init_models_wrap):
    async with TestingSessionLocal() as session:
        repo = UsersRepository(session)
        email = "spidey@example.com"
        new_password = "newpassword"

        user = await repo.reset_password(email, new_password)
        assert user.hashed_password == new_password

        await repo.confirmed_email(email)
        user = await repo.get_user_by_email(email)
        assert user.confirmed is True


@pytest.mark.asyncio
async def test_update_avatar(init_models_wrap):
    async with TestingSessionLocal() as session:
        repo = UsersRepository(session)
        email = "spidey@example.com"
        new_avatar = "https://avatar.example.com/new_spidey.png"

        user = await repo.update_avatar_url(email, new_avatar)
        assert user.avatar == new_avatar
