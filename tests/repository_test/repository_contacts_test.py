from unittest.mock import patch, Mock
from datetime import date
from src.repository.contacts import ContactRepository
from src.database.models import User, Contact
from src.schemas import ContactModel
from tests.conftest import TestingSessionLocal
import pytest


contact2 = ContactModel(
    first_name="John",
    second_name="Doe",
    email="john@example.com",
    phone_number="+380501234567",
    birthday=date(2000, 1, 1),
)

contact_update = ContactModel(
    first_name="John2",
    second_name="Doe",
    email="john@example.com",
    phone_number="+380501234567",
    birthday=date(2000, 1, 1),
)


@pytest.mark.asyncio
async def test_get_contacts(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)
        contact1 = Contact(
            first_name="John",
            second_name="Doe",
            email="john@example.com",
            phone_number="+380501234567",
            birthday=date.today(),
            user_id=user.id
        )
        session.add_all([contact1, contact1])
        await session.commit()

        repo = ContactRepository(session)
        result = await repo.get_contacts(skip=0, limit=10, user=user)
        assert len(result) == 1
        assert result[0].first_name == contact1.first_name


@pytest.mark.asyncio
async def test_get_contact_by_id(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)

        repo = ContactRepository(session)
        result = await repo.get_contact_by_id(contact_id=1, user=user)
        assert result.first_name == "John"


@pytest.mark.asyncio
async def test_create_contact(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)
        

        repo = ContactRepository(session)
        created = await repo.create_contact(body=contact2, user=user)
        result = await repo.get_contacts(skip=0, limit=10, user=user)
        assert created.first_name == contact2.first_name
        assert result[1].first_name == contact2.first_name


@pytest.mark.asyncio
async def test_update_contact(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)
        

        repo = ContactRepository(session)
        updated = await repo.update_contact(contact_id=1, body=contact_update, user=user)
        assert updated.first_name == contact_update.first_name


@pytest.mark.asyncio
async def test_remove_contact(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)

        repo = ContactRepository(session)
        removed = await repo.remove_contact(contact_id=1, user=user)
        assert removed.first_name == contact_update.first_name


@pytest.mark.asyncio
async def test_search_contact(init_models_wrap):
    async with TestingSessionLocal() as session:
        user = await session.get(User, 1)

        repo = ContactRepository(session)
        found = await repo.search_contacts(first_name="John", user=user)
        assert len(found)>0
        assert found[0].first_name == "John"
