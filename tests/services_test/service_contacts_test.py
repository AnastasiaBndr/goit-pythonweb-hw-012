import pytest
from datetime import date
from unittest.mock import patch, Mock, AsyncMock

from src.services.contacts import ContactService
from src.repository.contacts import ContactRepository
from src.database.models import User
from src.database.db import get_db
from src.schemas import ContactModel


@pytest.mark.asyncio
class TestContactService:

    @pytest.fixture
    def service(self):
        return ContactService(get_db)

    @pytest.fixture
    def user(self):
        return Mock(spec=User)

    async def test_get_contacts(self, service, user):
        fake_contacts = [
            "cont1",
            "cont2"
        ]

        with patch.object(ContactRepository, "get_contacts", new=AsyncMock(return_value=fake_contacts)):
            result = await service.get_contacts(skip=0, limit=10, user=user)

        assert result == fake_contacts

    async def test_get_contact(self, service, user):
        fake_contact = {"id": 1, "name": "Test"}

        with patch.object(ContactRepository, "get_contact_by_id", new=AsyncMock(return_value=fake_contact)):
            result = await service.get_contact(contact_id=1, user=user)

        assert result == fake_contact

    async def test_create_contact(self, service, user):
        body = ContactModel(
            first_name="Name",
            second_name="Second",
            email="email@gmail.com",
            phone_number="+380997778899",
            birthday=date.today(),
            additional_data=None,
        )

        fake_created = {"id": 10, "first_name": "Name"}

        with patch.object(ContactRepository, "create_contact", new=AsyncMock(return_value=fake_created)):
            result = await service.create_contact(body=body, user=user)

        assert result == fake_created

    async def test_update_contact(self, service, user):
        body = ContactModel(
            first_name="Alice",
            second_name="Smith",
            email="alice@gmail.com",
            phone_number="+380991234567",
            birthday=date.today(),
            additional_data=None,
        )

        fake_updated = {"id": 1, "first_name": "Alice"}

        with patch.object(ContactRepository, "update_contact", new=AsyncMock(return_value=fake_updated)):
            result = await service.update_contact(contact_id=1, body=body, user=user)

        assert result == fake_updated

    async def test_delete_contact(self, service, user):
        fake_deleted = {"status": "deleted"}

        with patch.object(ContactRepository, "remove_contact", new=AsyncMock(return_value=fake_deleted)):
            result = await service.delete_contact(contact_id=1, user=user)

        assert result == fake_deleted

    async def test_search_contact(self, service, user):
        fake_results = ["match1", "match2"]

        with patch.object(ContactRepository, "search_contacts", new=AsyncMock(return_value=fake_results)):
            result = await service.search_contact(first_name="Name", user=user)

        assert result == fake_results

    async def test_get_upcoming_birthdays(self, service, user):
        fake_birthdays = ["contact1"]

        with patch.object(ContactRepository, "get_upcoming_birthdays", new=AsyncMock(return_value=fake_birthdays)):
            result = await service.get_upcoming_birthdays(user=user)

        assert result == fake_birthdays
