"""
User management service.

Handles registration, retrieval, email confirmation, password reset,
and avatar updates for users.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.repository.users import UsersRepository
from src.security.hashing import Hash
from src.schemas import UserCreate

hash_handler = Hash()


class UserService:
    """
    Service layer for user operations.

    Parameters
    ----------
    db : AsyncSession
        SQLAlchemy async session.
    """

    def __init__(self, db: AsyncSession):
        self.repo = UsersRepository(db)

    async def register_user(self, body: UserCreate):
        """Register a new user with hashed password and optional Gravatar avatar."""
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)
        exist = await self.repo.get_user_by_username(body.username)
        if exist:
            return None

        hashed = hash_handler.get_password_hash(body.password)
        return await self.repo.create_user(body, hashed, avatar)

    async def get_user_by_id(self, user_id: int):
        """Retrieve a user by their ID."""
        return await self.repo.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """Retrieve a user by username."""
        return await self.repo.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """Retrieve a user by email."""
        return await self.repo.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """Mark a user's email as confirmed."""
        return await self.repo.confirmed_email(email)

    async def reset_password(self, email: str, password: str):
        """Reset a user's password with hashed password."""
        hashed = hash_handler.get_password_hash(password)
        return await self.repo.reset_password(email, hashed)

    async def update_avatar_url(self, email: str, url: str):
        """Update the avatar URL for a user."""
        return await self.repo.update_avatar_url(email, url)
