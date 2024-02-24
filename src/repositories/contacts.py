from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import Contact, User
from typing import List, Type
from sqlalchemy import or_, func, Date, and_


async def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Fetches a paginated list of contacts associated with a given user.

    Parameters:
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.
        user (User): The user object whose contacts are to be fetched.
        db (Session): The database session.

    Returns:
        List[Contact]: A list of contacts belonging to the user.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User,  db: Session) -> Contact:
    """
    Retrieves a single contact by its ID for a specified user.

    Parameters:
        contact_id (int): The ID of the contact to retrieve.
        user (User): The user object to match the contact against.
        db (Session): The database session.

    Returns:
        Contact: The contact object if found, otherwise None.
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: Contact, user: User, db: Session) -> Contact:
    """
    Creates a new contact record in the database for the specified user.

    Parameters:
        body (Contact): The contact details to be saved.
        user (User): The user object associated with the new contact.
        db (Session): The database session.

    Returns:
        Contact: The newly created contact object.
    """
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
    """
    Updates an existing contact's details if it belongs to the specified user.

    Parameters:
        contact_id (int): The ID of the contact to update.
        body (Contact): The updated contact details.
        user (User): The user object to match the contact against.
        db (Session): The database session.

    Returns:
        Contact | None: The updated contact object if found and updated, otherwise None.
    """
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
    """
    Deletes a contact by its ID if it belongs to the specified user.

    Parameters:
        contact_id (int): The ID of the contact to delete.
        user (User): The user object to match the contact against.
        db (Session): The database session.

    Returns:
        Contact | None: The deleted contact object if found and deleted, otherwise None.
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()

    return contact


async def search_contact(query: str, db: Session) -> list[Type[Contact]]:
    """
    Searches for contacts based on a query string.

    Parameters:
        query (str): The search query matching any part of the contact's first name, last name, or email.
        db (Session): The database session.

    Returns:
        list[Type[Contact]]: A list of contacts matching the search query.
    """
    return db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f'%{query}%'),
            Contact.last_name.ilike(f'%{query}%'),
            Contact.email.ilike(f'%{query}%')
        )
    ).all()


async def get_contacts_with_upcoming_birthdays(db: Session) -> List[Contact]:
    """
    Retrieves contacts with birthdays occurring within the next week.

    Parameters:
        db (Session): The database session.

    Returns:
        List[Contact]: A list of contacts with upcoming birthdays.
    """
    today = datetime.now()
    in_a_week = today + timedelta(days=7)

    upcoming_birthdays = db.query(Contact).filter(
        func.extract('month', func.cast(Contact.birth_date, Date)) == today.month,
        func.extract('day', func.cast(Contact.birth_date, Date)) >= today.day,
        func.extract('day', func.cast(Contact.birth_date, Date)) <= in_a_week.day
    ).all()

    return upcoming_birthdays
