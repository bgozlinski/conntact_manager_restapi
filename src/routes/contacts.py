from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas.contacts import Contact
from src.schemas.users import UserModel
from src.database.db import get_db
from src.repositories import contacts as repository_contacts
from src.services.auth import auth_service

from fastapi_limiter.depends import RateLimiter


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[Contact], description='No more than 3 requests per minute',
            dependencies=[Depends(RateLimiter(times=3, seconds=60))])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip=skip, limit=limit, user=current_user, db=db)
    return contacts


@router.get("/search", response_model=List[Contact])
async def search_contacts(query: str, db: Session = Depends(get_db)):
    contacts = await repository_contacts.search_contact(query=query, db=db)
    return contacts


@router.get("/upcoming-birthdays", response_model=List[Contact])
async def read_contacts_with_upcoming_birthdays(db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts_with_upcoming_birthdays(db=db)
    return contacts


@router.get("/{id}", response_model=Contact)
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id=contact_id, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=Contact, status_code=status.HTTP_201_CREATED)
async def create_contact(body: Contact, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body=body, user=current_user, db=db)


@router.put("/{id}", response_model=Contact)
async def update_contact(body: Contact, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id=body.id, body=body, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{id}", response_model=Contact)
async def delete_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contact_id=contact_id, user=current_user, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact
