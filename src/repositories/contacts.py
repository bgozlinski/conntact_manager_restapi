from sqlalchemy.orm import Session
from src.database.models import Contact
from typing import List
from sqlalchemy import or_


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: Contact, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      phone_number=body.phone_number,
                      birth_date=body.birth_date,
                      additional_info=body.additional_info
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: Contact, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birth_date = body.birth_date
        contact.additional_info = body.additional_info
        db.commit()

    return contact


async def delete_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id ==contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def search_contact(query: str, db: Session) -> List[Contact]:
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).all()
