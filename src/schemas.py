from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date


class ContactBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_info: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    class Config:
        orm_mode = True
