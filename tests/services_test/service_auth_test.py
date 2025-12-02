import pytest
from jose import jwt, JWTError
from datetime import timedelta
from unittest.mock import patch,AsyncMock, MagicMock
from src.database.models import User
from src.services.auth import get_current_user,create_email_token, AuthService
from src.conf.config import settings

@pytest.mark.asyncio
async def test_get_current_user():
    name ="name"
    fake_user=User(id=1,username=name)
    fake_token="fake.jwt.token"

    with patch("src.services.auth.jwt.decode", return_value={"sub": name}) as mock_jwt, \
         patch("src.services.auth.UsersRepository") as mock_repo:

        mock_repo_instance = mock_repo.return_value
        mock_repo_instance.get_user_by_username=AsyncMock(return_value=fake_user)

        result = await get_current_user(token=fake_token,db=MagicMock())

        assert result==fake_user
        mock_jwt.assert_called_once()
        mock_repo_instance.get_user_by_username.assert_called_once_with(
            name)
    

        assert result==fake_user

def create_email_token(data: dict):
    data={"sub":"user@gmail.com"}

    with patch("src.services.auth.jwt.encode", return_value="fake_token") as mock_jwt:
            
        token = create_email_token(data)
        assert token == "fake_token"
        mock_jwt.assert_called_once()


@pytest.mark.asyncio
class TestAuthService:

    @pytest.fixture
    def service(self):
        return AuthService()
    
    @pytest.fixture
    def data(self):
        return {"sub":"test"}
    
    async def test_create_token(self,service,data):
        with patch("src.services.auth.jwt.encode") as mock_encode:
            mock_encode.return_value="encoded_token"

            token=service._create_token(
                data=data,
                expires_delta=timedelta(minutes=5),
                token_type="access"
            )

            assert token=="encoded_token"
            assert mock_encode.called

    async def test_create_access_token(self,data,service):
        with patch.object(service,"_create_token",return_value="access") as mock_ct:
            token = await service.create_access_token(data)

            assert token == "access"
            mock_ct.assert_called_once()

            args, kwargs = mock_ct.call_args
            assert args[1] == timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    async def test_create_refresh_token(self,data,service):
        with patch.object(service, "_create_token", return_value="refresh123") as mock_ct:
            token = await service.create_refresh_token(data)

            assert token == "refresh123"
            mock_ct.assert_called_once()
            args, kwargs = mock_ct.call_args
            assert args[1] == timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    async def test_verify_refresh_token_valid(self, service):
        refresh_token = "valid_token"

        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "testuser",
                "token_type": "refresh"
            }

            fake_user = User(username="testuser", refresh_token=refresh_token)

            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = fake_user

            mock_db = AsyncMock()
            mock_db.execute.return_value = mock_result

            user = await service.verify_refresh_token(refresh_token, mock_db)

            assert user == fake_user
            mock_db.execute.assert_called_once()


    async def test_verify_refresh_token_invalid_signature(self,service):
        with patch("src.services.auth.jwt.decode", side_effect=JWTError):
            user = await service.verify_refresh_token("bad_token", AsyncMock())
            assert user is None


    async def test_verify_refresh_token_wrong_type(self,service):
        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "test",
                                        "token_type": "access"} 

            user = await service.verify_refresh_token("token", AsyncMock())
            assert user is None


    async def test_get_email_from_token_valid(self,service):
        with patch("src.services.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "email@example.com"}

            email = await service.get_email_from_token("token")
            assert email == "email@example.com"


    async def test_get_email_from_token_invalid(self,service):
        with patch("src.services.auth.jwt.decode", side_effect=JWTError):
            email = await service.get_email_from_token("token")
            assert email is None
