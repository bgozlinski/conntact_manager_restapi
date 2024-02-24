from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    """
    A base model for contact information, serving as a foundation for more specific contact models.

    Attributes:
        first_name (str): The first name of the contact.
        last_name (str): The last name of the contact.
        email (EmailStr): The email address of the contact. Must be a valid email format.
        phone_number (str): The contact's phone number as a string.
        birth_date (date): The birthdate of the contact.
        additional_info (Optional[str]): Optional additional information about the contact; defaults to None.

    This base model includes essential fields for contact management systems, allowing for extension and customization.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_info: Optional[str] = None


class ContactModel(ContactBase):
    """
    A detailed model for a contact, extending the base contact model with an identifier.

    Attributes:
        id (int): A unique identifier for the contact, typically used as a primary key in databases.
        Inherits all attributes from ContactBase.

    The Contact model is used for read operations where the contact's ID is necessary, following Pydantic's ORM mode
    to facilitate ORM object serialization.

    Config:
        orm_mode (bool): Enables ORM mode for Pydantic models, allowing the model to be returned directly from ORM queries.
    """
    id: int

    class Config:
        orm_mode = True
