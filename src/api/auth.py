from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import BackgroundTasks

from src.schemas import UserCreate
from src.database.db import get_db
from src.services.users import UserService
from src.services.auth import AuthService
from src.services.email import send_email
from src.security.hashing import Hash
from src.schemas import TokenModel, TokenRefreshRequest, RequestEmail, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
hash_handler = Hash()
auth_service = AuthService()


@router.post("/register")
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(body.email)

    if email_user:
        raise HTTPException(status_code=409, detail="Account already exists")

    username_user = await user_service.get_user_by_username(body.username)
    if username_user:
        raise HTTPException(status_code=409, detail="Account already exists")
    new_user = await user_service.register_user(body)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        "email": new_user.email,
        "username": new_user.username,
        "created_at": new_user.created_at,
    }


@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form.username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not hash_handler.verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email wasn`t confirmed",
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
    user = await auth_service.verify_refresh_token(request.refresh_token, db)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
        )
    new_access_token = await auth_service.create_access_token(
        data={"sub": user.username}
    )
    return {
        "access_token": new_access_token,
        "refresh_token": request.refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email has elready been confirmed",
        )
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed!"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Ваша електронна пошта вже підтверджена"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}
