from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.sql import crud

from src.schemas import Contact
from src.database.db import get_db
from src.repositories import contacts as repository_contacts

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[Contact])
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip=skip, limit=limit, db=db)
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
async def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id=contact_id, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=Contact)
async def create_contact(body: Contact, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body=body, db=db)


@router.put("/{id}", response_model=Contact)
async def update_contact(body: Contact, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id=body.id, body=body, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{id}", response_model=Contact)
async def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.delete_contact(contact_id=contact_id, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact



