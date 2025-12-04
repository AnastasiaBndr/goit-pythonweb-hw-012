"""
Application settings module.

Defines configuration parameters for the application, including:
- Database connection
- JWT authentication
- Mail server
- Cloudinary credentials
- Redis cache

Uses Pydantic BaseSettings to automatically load environment variables
from a `.env` file.
"""

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings.

    Attributes
    ----------
    DB_URL : str
        Database connection URL.
    JWT_SECRET : str
        Secret key for JWT token generation.
    JWT_ALGORITHM : str
        Algorithm for JWT encoding (default "HS256").
    REFRESH_TOKEN_EXPIRE_MINUTES : int
        Expiration time for refresh tokens in minutes (default 30).
    ACCESS_TOKEN_EXPIRE_MINUTES : int
        Expiration time for access tokens in minutes (default 30).

    MAIL_USERNAME : EmailStr
        Mail server username.
    MAIL_PASSWORD : str
        Mail server password.
    MAIL_FROM : EmailStr
        Email address for sending emails.
    MAIL_PORT : int
        Mail server port.
    MAIL_SERVER : str
        Mail server address.
    MAIL_FROM_NAME : str
        Sender name for emails.
    MAIL_STARTTLS : bool
        Whether to use STARTTLS for mail connection.
    MAIL_SSL_TLS : bool
        Whether to use SSL/TLS for mail connection.
    USE_CREDENTIALS : bool
        Whether to use credentials for mail authentication.
    VALIDATE_CERTS : bool
        Whether to validate mail server SSL certificates.

    CLD_NAME : str
        Cloudinary cloud name.
    CLD_API_KEY : int
        Cloudinary API key.
    CLD_API_SECRET : str
        Cloudinary API secret.

    REDIS_HOST : str
        Redis server host.
    REDIS_PASSWORD : str
        Redis server password.
    """

    POSTGRES_DB:str
    POSTGRES_PASSWORD:str
    POSTGRES_USER:str
    POSTGRES_PORT:int
    POSTGRES_HOST:str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 30
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLD_NAME: str = "name"
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    REDIS_HOST: str
    REDIS_PASSWORD: str

    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
