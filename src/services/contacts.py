"""
Contact management service.

Provides high-level CRUD operations and search functionality
for contacts, delegating database interactions to ContactRepository.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel
from src.database.models import User


class ContactService:
    """
    Service layer for contact-related operations.

    Parameters
    ----------
    db : AsyncSession
        SQLAlchemy async session for database access.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repository = ContactRepository(db)

    async def get_contacts(self, skip: int, limit: int, user: User):
        """Retrieve a list of contacts for the user with pagination."""
        return await self.repository.get_contacts(skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """Retrieve a specific contact by ID for the given user."""
        return await self.repository.get_contact_by_id(contact_id, user)

    async def create_contact(self, body: ContactModel, user: User):
        """Create a new contact for the user."""
        return await self.repository.create_contact(body, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        """Update an existing contact for the user."""
        return await self.repository.update_contact(contact_id, body, user)

    async def delete_contact(self, contact_id, user: User):
        """Delete a contact for the user."""
        return await self.repository.remove_contact(contact_id, user)

    async def search_contact(
        self, first_name: str = None, second_name: str = None, email: str = None, user: User = None
    ):
        """Search contacts by first name, second name, or email."""
        return await self.repository.search_contacts(first_name, second_name, email, user)

    async def get_upcoming_birthdays(self, user: User):
        """Get contacts with upcoming birthdays for the user."""
        return await self.repository.get_upcoming_birthdays(user)
