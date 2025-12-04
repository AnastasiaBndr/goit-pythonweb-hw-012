"""
User profile and administration API endpoints.

This module contains routes related to user profile access, avatar updates,
admin-restricted operations, and rate-limited user information retrieval.

Features
--------

* Retrieve current user data (with Redis caching)
* Update user avatar (Cloudinary upload)
* Public endpoint (open to all)
* Admin-only endpoint

Integrations
------------

* ``UserService`` – user management
* ``UploadFileService`` – file storage handler
* ``get_current_user`` / ``get_current_admin_user`` – authentication
* Redis – caching of user data
* ``slowapi`` – rate limiting
"""

import redis
import json
from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
import time

from src.database.db import get_db
from src.schemas import UserResponse
from src.database.models import User
from src.services.auth import get_current_user, get_current_admin_user
from src.services.upload_file import UploadFileService
from src.services.users import UserService
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

# r = redis.Redis(
#     host=settings.REDIS_HOST,
#     port=6379,
#     password=settings.REDIS_PASSWORD,
#     db=0,
# )

cache = {}

CACHE_EXPIRATION = 60

@router.get(
    "/me",
    response_model=UserResponse,
    description="No more than 10 requests per minute",
)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get the current user's profile information.

    This endpoint returns authenticated user's data with Redis caching.
    Cached results expire after 60 seconds.  
    The endpoint is rate-limited: **10 requests per minute per IP**.

    Parameters
    ----------
    request : Request
        Current request object (required by slowapi).
    user : User
        Authenticated user retrieved via dependency injection.

    Returns
    -------
    UserResponse
        User profile data loaded from cache or database.
    """
    # cached_user = r.get(str(f"user:{user.id}"))
    # if cached_user:
    #     return json.loads(cached_user)

    # user_response = UserResponse.model_validate(user)
    # user_data = user_response.model_dump()

    # r.setex(f"user:{user.id}", 60, json.dumps(user_data))

    # return user_data
    cached_entry = cache.get(user.id)
    if cached_entry:
        data, timestamp = cached_entry
        if time.time() - timestamp < CACHE_EXPIRATION:
            return data  # повертаємо кешовані дані

    # Якщо немає або прострочено — беремо з бази
    user_response = UserResponse.model_validate(user)
    user_data = user_response.model_dump()

    # Кешуємо результат
    cache[user.id] = (user_data, time.time())

    return user_data


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the authenticated admin user's avatar.

    This endpoint uploads the avatar image to Cloudinary via
    ``UploadFileService`` and stores the new URL in the database.

    Parameters
    ----------
    file : UploadFile
        Image file uploaded by the client.
    user : User
        Authenticated admin user (admin rights required).
    db : AsyncSession
        Database session.

    Returns
    -------
    UserResponse
        The updated user data including the new avatar URL.
    """
    upload_service = UploadFileService(
        settings.CLD_NAME,
        settings.CLD_API_KEY,
        settings.CLD_API_SECRET,
    )
    avatar_url = upload_service.upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user


@router.get("/public")
def read_public():
    """
    Publicly accessible endpoint.

    Returns
    -------
    dict
        A simple greeting message.
    """
    return {"message": "Public!"}


@router.get("/admin")
def read_admin(current_user: User = Depends(get_current_admin_user)):
    """
    Admin-only endpoint.

    Parameters
    ----------
    current_user : User
        Currently authenticated admin user.

    Returns
    -------
    dict
        A greeting message including the admin username.
    """
    return {"message": f"Greetings, {current_user.username}! This is admin route"}
