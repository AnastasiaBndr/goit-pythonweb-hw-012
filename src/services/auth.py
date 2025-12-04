"""
Authentication and authorization utilities.

This module provides core authentication logic including:

* JWT token creation (access, refresh, email confirmation)
* Token validation and decoding
* Current user retrieval via OAuth2
* Admin-role access enforcement
* AuthService class for reusable token operations

Integrations
------------

* ``UsersRepository`` – user retrieval from database
* ``User`` SQLAlchemy model
* ``UserRole`` enum for role-based access
* ``FastAPI`` OAuth2PasswordBearer for bearer token authentication
* ``python-jose`` for JWT handling
"""

from datetime import datetime, timedelta, UTC
from fastapi import HTTPException, Depends
from typing import Optional, Literal
from sqlalchemy import select, and_
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from src.repository.users import UsersRepository
from src.database.db import get_db
from src.database.models import User
from src.conf.config import settings
from src.database.models import UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/goithomework12/api/auth/login")
secret_key = settings.JWT_SECRET
algorithm = settings.JWT_ALGORITHM
access_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
refresh_expire = settings.REFRESH_TOKEN_EXPIRE_MINUTES


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Retrieve the currently authenticated user based on the provided JWT token.

    The function:
    - Validates the JWT token
    - Extracts the username from the payload
    - Fetches the corresponding user from the database

    Parameters
    ----------
    token : str
        JWT access token extracted from the Authorization header.
    db : AsyncSession
        Database session dependency.

    Returns
    -------
    User
        The authenticated user record.

    Raises
    ------
    HTTPException
        If the token is invalid or the user does not exist.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="User not found")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    repo = UsersRepository(db)
    user = await repo.get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    """
    Ensure that the current user has administrator privileges.

    Parameters
    ----------
    current_user : User
        User retrieved via :func:`get_current_user`.

    Returns
    -------
    User
        The validated admin user.

    Raises
    ------
    HTTPException
        If the user does not have admin permissions.
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No access rights")
    return current_user


def create_email_token(data: dict):
    """
    Generate a time-limited email verification token.

    The token includes:
    - ``iat`` – issued-at timestamp
    - ``exp`` – expiration timestamp (7 days)

    Parameters
    ----------
    data : dict
        Additional payload to encode in the token.

    Returns
    -------
    str
        Encoded JWT email confirmation token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET,
                       algorithm=settings.JWT_ALGORITHM)
    return token


class AuthService:
    """
    Service class providing authentication-related JWT operations.

    This class handles:
    - Access token generation
    - Refresh token generation
    - Token type differentiation
    - Token verification
    - Extracting email from verification tokens
    """

    def _create_token(
        self,
        data: dict,
        expires_delta: timedelta,
        token_type: Literal["access", "refresh"],
    ):
        """
        Internal helper that creates a signed JWT token.

        Parameters
        ----------
        data : dict
            Payload data to encode.
        expires_delta : timedelta
            Time delta after which the token expires.
        token_type : {"access", "refresh"}
            Specifies the type of the created token.

        Returns
        -------
        str
            Encoded JWT token.
        """
        to_encode = data.copy()
        now = datetime.now(UTC)
        expire = now + expires_delta
        to_encode.update({"exp": expire, "iat": now, "token_type": token_type})
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Create an access token for the user.

        Parameters
        ----------
        data : dict
            Payload containing user identity (usually ``{"sub": username}``).
        expires_delta : float, optional
            Custom expiration time in minutes. Default uses settings.

        Returns
        -------
        str
            Encoded JWT access token.
        """
        if expires_delta:
            access_token = self._create_token(data, expires_delta, "access")
        else:
            access_token = self._create_token(
                data, timedelta(minutes=access_expire), "access"
            )
        return access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ):
        """
        Create a refresh token for the user.

        Parameters
        ----------
        data : dict
            User payload identifying the subject.
        expires_delta : float, optional
            Custom expiration time. If none provided, default is used.

        Returns
        -------
        str
            Encoded JWT refresh token.
        """
        if expires_delta:
            refresh_token = self._create_token(data, expires_delta, "refresh")
        else:
            refresh_token = self._create_token(
                data, timedelta(minutes=refresh_expire), "refresh"
            )
        return refresh_token

    async def verify_refresh_token(self, refresh_token: str, db: AsyncSession):
        """
        Validate and decode the refresh token.

        Steps:
        - Decode token
        - Validate token type (must be ``refresh``)
        - Fetch user whose stored refresh token matches

        Parameters
        ----------
        refresh_token : str
            The refresh token provided by the client.
        db : AsyncSession
            Database session.

        Returns
        -------
        User or None
            The authenticated user, or ``None`` if validation fails.
        """
        try:
            payload = jwt.decode(refresh_token, secret_key,
                                 algorithms=[algorithm])
            username: str = payload.get("sub")
            token_type: str = payload.get("token_type")
            if username is None or token_type != "refresh":
                return None
            stmt = select(User).where(
                and_(User.username == username,
                     User.refresh_token == refresh_token)
            )
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()

            return user
        except JWTError:
            return None

    async def get_email_from_token(self, token: str):
        """
        Extract an email address from an email confirmation token.

        Parameters
        ----------
        token : str
            Encoded JWT token.

        Returns
        -------
        str or None
            Email address if token is valid, otherwise ``None``.
        """
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            email = payload["sub"]
            return email
        except JWTError:
            return None
