import redis
import json
from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.schemas import UserResponse
from src.database.models import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)
r = redis.Redis(host=settings.REDIS_HOST, port=6379,
                password=settings.REDIS_PASSWORD, db=0)


@router.get(
    "/me",
    response_model=UserResponse,
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    cached_user = r.get(str(f"user:{user.id}"))
    if cached_user:

        return json.loads(cached_user)

    user_response = UserResponse.model_validate(user)
    user_data = user_response.model_dump()

    r.setex(f"user:{user.id}", 60, json.dumps(user_data))
    print(r.keys("*"))

    return user_data


...


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    upload_service = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    )
    avatar_url = upload_service.upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.get("/public")
def read_public():
    return {"message": "Public!"}


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    return {"message": f"Greetings, {current_user.username}! This is admin route"}
