from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user

from src.database.models import Contact, User
from typing import List, Type
from sqlalchemy import or_, func, Date, and_


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()
    # return db.query(Contact).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User,  db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    # return db.query(Contact).filter(Contact.id == contact_id).first()


async def create_contact(body: Contact, user: User, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      phone_number=body.phone_number,
                      birth_date=body.birth_date,
                      additional_info=body.additional_info,
                      user_id=user.id
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: Contact, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birth_date = body.birth_date
        contact.additional_info = body.additional_info
        db.commit()

    return contact


async def delete_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def search_contact(query: str, db: Session) -> list[Type[Contact]]:
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).all()


async def get_contacts_with_upcoming_birthdays(db: Session) -> List[Contact]:
    today = datetime.now()
    in_a_week = today + timedelta(days=7)

    upcoming_birthdays = db.query(Contact).filter(
        func.extract('month', func.cast(Contact.birth_date, Date)) == today.month,
        func.extract('day', func.cast(Contact.birth_date, Date)) >= today.day,
        func.extract('day', func.cast(Contact.birth_date, Date)) <= in_a_week.day
    ).all()

    return upcoming_birthdays
