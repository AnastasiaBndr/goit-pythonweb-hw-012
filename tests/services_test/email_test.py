import pytest
from unittest.mock import patch, MagicMock,AsyncMock
from fastapi_mail.errors import ConnectionErrors
from src.services.email import send_email


@pytest.mark.asyncio
async def test_send_email_token():
    fake_token="token"
    
    with patch("src.services.email.create_email_token",return_value=fake_token) as mock_token,\
            patch("src.services.email.FastMail") as mock_fastmail:
        mock_fm_instance = MagicMock()
        mock_fastmail.return_value = mock_fm_instance
        mock_fm_instance.send_message = AsyncMock()
        
        await send_email(
            email="test@gmail.com",
            username="username",
            host="host",
            template_name="template_name",
            subject="subject",
        )

        mock_token.assert_called_once()

        mock_fastmail.assert_called_once()

        mock_fm_instance.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_token_connection_error():
    fake_token = "token"

    with patch("src.services.email.create_email_token", return_value=fake_token), \
            patch("src.services.email.FastMail") as mock_fastmail:
        mock_fm_instance = MagicMock()
        mock_fastmail.return_value = mock_fm_instance
        mock_fm_instance.send_message = AsyncMock(side_effect=ConnectionErrors("Error"))

        await send_email(
            email="test@gmail.com",
            username="username",
            host="host",
            template_name="template_name",
            subject="subject",
        )

        mock_fastmail.assert_called_once()

        mock_fm_instance.send_message.assert_awaited_once()