"""
Email sending utility using FastAPI-Mail.

Handles sending verification and password reset emails with templating support.
"""

from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.meta.ua",
    MAIL_FROM_NAME="Example email",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str, template_name: str, subject: str):
    """
    Send an email to the specified recipient using a template.

    Parameters
    ----------
    email : EmailStr
        Recipient email address.
    username : str
        Recipient's username for template personalization.
    host : str
        Base URL used in email templates.
    template_name : str
        Name of the template file.
    subject : str
        Email subject line.

    Raises
    ------
    ConnectionErrors
        If sending the email fails due to connection issues.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name)
    except ConnectionErrors as err:
        print(err)
