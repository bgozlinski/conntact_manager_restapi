from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.contacts import ContactModel
from src.database.db import get_db
from src.repositories import contacts as repository_contacts
from src.services.auth import auth_service

from fastapi_limiter.depends import RateLimiter


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactModel], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a paginated list of contacts for the current authenticated user.

    Parameters:
        skip (int): Number of records to skip for pagination.
        limit (int): Maximum number of records to return.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user obtained via dependency.

    Returns:
        List[Contact]: A list of contact objects.
    """
    contacts = await repository_contacts.get_contacts(skip=skip, limit=limit, user=current_user, db=db)
    return contacts


@router.get("/search", response_model=List[ContactModel])
async def search_contacts(query: str, db: Session = Depends(get_db)):
    """
    Searches for contacts based on a query string.

    Parameters:
        query (str): Search query matching contact's name or details.
        db (Session): Database session dependency.

    Returns:
        List[Contact]: A list of contacts matching the search query.
    """
    contacts = await repository_contacts.search_contact(query=query, db=db)
    return contacts


@router.get("/upcoming-birthdays", response_model=List[ContactModel])
async def read_contacts_with_upcoming_birthdays(db: Session = Depends(get_db)):
    """
    Retrieves contacts with upcoming birthdays within the next week.

    Parameters:
        db (Session): Database session dependency.

    Returns:
        List[Contact]: A list of contacts with upcoming birthdays.
    """
    contacts = await repository_contacts.get_contacts_with_upcoming_birthdays(db=db)
    return contacts


@router.get("/{id}", response_model=ContactModel)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves a single contact by its ID for the current authenticated user.

    Parameters:
        contact_id (int): The unique identifier of the contact.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user obtained via dependency.

    Returns:
        Contact: The contact object if found.

    Raises:
        HTTPException: 404 error if the contact is not found.
    """
    contact = await repository_contacts.get_contact(contact_id=contact_id, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactModel, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Creates a new contact for the current authenticated user.

    Parameters:
        body (Contact): Contact creation data.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user obtained via dependency.

    Returns:
        Contact: The newly created contact object.
    """
    return await repository_contacts.create_contact(body=body, user=current_user, db=db)


@router.put("/{id}", response_model=ContactModel)
async def update_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Updates an existing contact for the current authenticated user.

    Parameters:
        body (Contact): Contact update data, including the contact ID.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user obtained via dependency.

    Returns:
        Contact: The updated contact object if found.

    Raises:
        HTTPException: 404 error if the contact to update is not found.
    """
    contact = await repository_contacts.update_contact(contact_id=body.id, body=body, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{id}", response_model=ContactModel)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Deletes a contact by its ID for the current authenticated user.

    Parameters:
        contact_id (int): The unique identifier of the contact to delete.
        db (Session): Database session dependency.
        current_user (User): The current authenticated user obtained via dependency.

    Returns:
        Contact: The deleted contact object if found.

    Raises:
        HTTPException: 404 error if the contact to delete is not found.
    """
    contact = await repository_contacts.delete_contact(contact_id=contact_id, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
