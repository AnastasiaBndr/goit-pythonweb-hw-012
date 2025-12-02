"""
Authentication and authorization API endpoints.

This module contains all authentication-related routes, including:

* User registration
* Login and token generation
* Refreshing JWT tokens
* Email confirmation
* Password reset logic

It integrates with:

* ``UserService`` – user management logic
* ``AuthService`` – JWT token generation & validation
* ``send_email`` – background email delivery
* ``Hash`` – password hashing/verification
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    BackgroundTasks,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import (
    UserCreate,
    TokenModel,
    TokenRefreshRequest,
    ResetPasswordSchema,
    RequestEmail,
    UserResponse,
)
from src.database.db import get_db
from src.services.users import UserService
from src.services.auth import AuthService
from src.services.email import send_email
from src.security.hashing import Hash

router = APIRouter(prefix="/auth", tags=["auth"])

hash_handler = Hash()
auth_service = AuthService()


@router.post("/register", status_code=201)
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.

    This endpoint creates a new user and sends a confirmation email
    in the background.

    Parameters
    ----------
    body : UserCreate
        User registration data.
    background_tasks : BackgroundTasks
        Background task manager for sending emails.
    request : Request
        Current request object.
    db : AsyncSession
        Database session (dependency).

    Raises
    ------
    HTTPException
        If a user with the given username or email already exists.

    Returns
    -------
    dict
        Basic information about the newly created user.
    """
    user_service = UserService(db)

    if await user_service.get_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="Account already exists")
    if await user_service.get_user_by_username(body.username):
        raise HTTPException(status_code=409, detail="Account already exists")

    new_user = await user_service.register_user(body)

    background_tasks.add_task(
        send_email,
        new_user.email,
        new_user.username,
        request.base_url,
        template_name="verify_email.html",
        subject="Confirm your email",
    )

    return {
        "email": new_user.email,
        "username": new_user.username,
        "created_at": new_user.created_at,
    }


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate a user and return access/refresh tokens.

    Parameters
    ----------
    form : OAuth2PasswordRequestForm
        Login credentials (username + password).
    db : AsyncSession
        Database session.

    Raises
    ------
    HTTPException
        If username doesn't exist, password is invalid,
        or the email is not confirmed.

    Returns
    -------
    dict
        Access token, refresh token, and token type.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")
    if not hash_handler.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email wasn't confirmed",
        )

    access_token = await auth_service.create_access_token({"sub": user.username})
    refresh_token = await auth_service.create_refresh_token({"sub": user.username})

    user.refresh_token = refresh_token
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", response_model=TokenModel)
async def new_token(request: TokenRefreshRequest, db: AsyncSession = Depends(get_db)):
    """
    Generate a new access token using a valid refresh token.

    Parameters
    ----------
    request : TokenRefreshRequest
        Refresh token payload.
    db : AsyncSession
        Database session.

    Raises
    ------
    HTTPException
        If the refresh token is invalid or expired.

    Returns
    -------
    dict
        New access token and original refresh token.
    """
    user = await auth_service.verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )

    new_access_token = await auth_service.create_access_token({"sub": user.username})

    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Send an email confirmation link to the user.

    If the email exists and is not confirmed, a verification email is sent.
    Otherwise, a generic message is returned (to avoid email enumeration).

    Parameters
    ----------
    body : RequestEmail
        Email address container.
    background_tasks : BackgroundTasks
        Background task manager.
    request : Request
        Current request context.
    db : AsyncSession
        Database session.

    Returns
    -------
    dict
        Status message.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        return {"message": "If this email exists, a confirmation link has been sent."}

    if user.confirmed:
        return {"message": "Your email is already confirmed."}

    background_tasks.add_task(
        send_email,
        user.email,
        user.username,
        request.base_url,
        template_name="verify_email.html",
        subject="Confirm your email",
    )
    return {"message": "If this email exists, a confirmation link has been sent."}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a user's email using a verification token.

    Parameters
    ----------
    token : str
        Email verification token.
    db : AsyncSession
        Database session.

    Raises
    ------
    HTTPException
        If the token is invalid or the user is already confirmed.

    Returns
    -------
    dict
        Confirmation message.
    """
    email = await auth_service.get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is None:
        raise HTTPException(status_code=400, detail="Verification error")
    if user.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Your email has already been confirmed",
        )

    await user_service.confirmed_email(email)
    return {"message": "Email confirmed!"}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    The endpoint always returns a generic message to avoid disclosing
    whether an email exists in the system.

    Parameters
    ----------
    body : RequestEmail
        Email for password reset.
    background_tasks : BackgroundTasks
        Background task manager.
    request : Request
        Current request object.
    db : AsyncSession
        Database session.

    Returns
    -------
    dict
        Status message.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        background_tasks.add_task(
            send_email,
            user.email,
            user.username,
            request.base_url,
            template_name="reset_password.html",
            subject="Reset password",
        )

    return {"message": "If this email exists, a reset link has been sent."}


@router.post("/reset_password")
async def reset_password(data: ResetPasswordSchema, db: AsyncSession = Depends(get_db)):
    """
    Reset the user's password using a valid token.

    Parameters
    ----------
    data : ResetPasswordSchema
        Token + new password payload.
    db : AsyncSession
        Database session.

    Raises
    ------
    HTTPException
        If the token is invalid or user does not exist.

    Returns
    -------
    dict
        Success message.
    """
    email = await auth_service.get_email_from_token(data.token)
    if email is None:
        raise HTTPException(status_code=400, detail="Verification error")

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if user is None:
        raise HTTPException(status_code=400, detail="Verification error")

    await user_service.reset_password(email, data.password)
    return {"message": "Password reset confirmed!"}
