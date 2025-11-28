from sqlalchemy import String, Date, Enum, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import date
from enum import Enum as PyEnum


class Base(DeclarativeBase):
    pass


class UserRole(str, PyEnum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(Date)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    user_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False)

    def __str__(self) -> str:
        return f"User: {self.username}"


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    second_name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)

    phone_number: Mapped[str] = mapped_column(String(13), nullable=False)
    birthday: Mapped[date] = mapped_column(Date)
    additional_data: Mapped[str] = mapped_column(String(200), nullable=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", backref="contacts")

    def __str__(self):
        return (
            f"Contact: ({self.id}, {self.first_name} "
            f"{self.second_name} {self.email} "
            f"{self.phone_number} {self.birthday} {self.additional_data})"
        )
