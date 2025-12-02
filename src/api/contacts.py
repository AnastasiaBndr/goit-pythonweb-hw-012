"""
Contacts management API endpoints.

This module provides CRUD operations for user contacts, including:

* Listing contacts with filtering options
* Viewing a single contact
* Creating new contacts
* Updating contacts
* Deleting contacts
* Getting upcoming birthdays

All endpoints require authentication and operate only on the
contacts belonging to the authenticated user.

It integrates with:

* ``ContactService`` – business logic for contacts
* ``AuthService`` / ``get_current_user`` – authentication layer
"""

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
    """
    Get a list of contacts belonging to the current user.

    Supports pagination and optional filtering by first name,
    second name, or email.

    Parameters
    ----------
    skip : int, default=0
        Number of records to skip (pagination).
    limit : int
        Maximum number of contacts to return (1–100).
    first_name : str | None
        Filter by contact first name.
    second_name : str | None
        Filter by contact second name.
    email : str | None
        Filter by contact email.
    db : AsyncSession
        Database session.
    user : User
        Currently authenticated user.

    Returns
    -------
    List[ContactResponse]
        A list of user contacts.
    """
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
    """
    Get contacts with upcoming birthdays in the next 7 days.

    Parameters
    ----------
    db : AsyncSession
        Database session.
    user : User
        Authenticated user.

    Returns
    -------
    List[ContactResponse]
        A list of contacts with soon birthdays.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a contact by its ID.

    Parameters
    ----------
    contact_id : int
        ID of the contact.
    db : AsyncSession
        Database session.
    user : User
        Authenticated user.

    Raises
    ------
    HTTPException
        If the contact does not exist.

    Returns
    -------
    ContactResponse
        The requested contact.
    """
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
    """
    Create a new contact for the authenticated user.

    Parameters
    ----------
    body : ContactModel
        Data for the new contact.
    db : AsyncSession
        Database session.
    user : User
        Authenticated user.

    Returns
    -------
    ContactResponse
        The newly created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update an existing contact.

    Parameters
    ----------
    contact_id : int
        ID of the contact to update.
    body : ContactUpdate
        Updated fields.
    db : AsyncSession
        Database session.
    user : User
        Authenticated user.

    Raises
    ------
    HTTPException
        If the contact does not exist.

    Returns
    -------
    ContactResponse
        The updated contact.
    """
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
    """
    Delete a contact by ID.

    Parameters
    ----------
    contact_id : int
        ID of the contact to delete.
    db : AsyncSession
        Database session.
    user : User
        Authenticated user.

    Raises
    ------
    HTTPException
        If the contact does not exist.

    Returns
    -------
    ContactResponse
        The deleted contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
