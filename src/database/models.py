"""
Database models module.

Defines User and Contact SQLAlchemy ORM models and
user role enumeration.
"""

from sqlalchemy import String, Date, Enum, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import date
from enum import Enum as PyEnum


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class UserRole(str, PyEnum):
    """Enumeration of possible user roles."""
    USER = "user"
    ADMIN = "admin"


class User(Base):
    """
    ORM model for users.

    Attributes
    ----------
    id : int
        Primary key.
    username : str
        Unique username.
    email : str
        User's email address.
    hashed_password : str
        Hashed password.
    created_at : date
        Date of account creation.
    refresh_token : str
        Refresh token for authentication.
    avatar : str
        URL to user avatar.
    confirmed : bool
        Whether the email is confirmed.
    user_role : UserRole
        Role of the user (USER or ADMIN).
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False
    )
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    user_role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"), default=UserRole.USER, nullable=False
    )

    def __str__(self) -> str:
        return f"User: {self.username}"


class Contact(Base):
    """
    ORM model for contacts.

    Attributes
    ----------
    id : int
        Primary key.
    first_name : str
        First name of the contact.
    second_name : str
        Second name of the contact.
    email : str
        Contact email address.
    phone_number : str
        Contact phone number.
    birthday : date
        Birthday of the contact.
    additional_data : str
        Any additional information about the contact.
    user_id : int
        Foreign key to the user who owns this contact.
    user : User
        SQLAlchemy relationship to the owning user.
    """
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    second_name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(13), nullable=False)
    birthday: Mapped[date] = mapped_column(Date)
