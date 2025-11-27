from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.contacts import ContactService
from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactUpdate, ContactResponse
from src.services.auth import AuthService, get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])
auth_service = AuthService()


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=1),
    first_name: Optional[str] = Query(None),
    second_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    service = ContactService(db)

    if first_name or second_name or email:
        contacts = await service.search_contact(first_name, second_name, email, user)
    else:
        contacts = await service.get_contacts(skip, limit, user)

    return contacts


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):

    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact = await ContactService(db).get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_Contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
