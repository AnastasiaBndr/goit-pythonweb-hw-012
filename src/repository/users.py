from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.database.models import User

from src.schemas import UserCreate


class UsersRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self, body: UserCreate, password: str, avatar: str
    ) -> User | None:
        today_date = datetime.now()
        user = User(
            username=body.username,
            email=body.email,
            hashed_password=password,
            created_at=today_date,
            avatar=avatar,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()
    
    async def update_avatar_url(self, email: str, url: str) -> User:
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

