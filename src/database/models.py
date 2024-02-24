from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, func, Boolean
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Contact(Base):
    """
    A Contact model representing a contact record in the database.

    Attributes:
        id (Column): Unique identifier for the contact.
        first_name (Column): First name of the contact.
        last_name (Column): Last name of the contact.
        email (Column): Email address of the contact, must be unique.
        phone_number (Column): Phone number of the contact.
        birth_date (Column): Date of birth of the contact.
        additional_info (Column): Additional information about the contact.
        user_id (Column): Foreign key to the User model.
        user (relationship): Relationship to the User model, backref to 'contacts'.
    """
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True)
    birth_date = Column(Date)
    additional_info = Column(Text, nullable=True)
    user_id = Column('user_id', ForeignKey('users.id', ondelete='CASCADE'), default=None)
    user = relationship('User', backref='contacts')


class User(Base):
    """
    A User model representing a user record in the database.

    Attributes:
        id (Column): Unique identifier for the user.
        username (Column): Username of the user.
        email (Column): Email address of the user, must be unique.
        password (Column): Hashed password for the user.
        created_at (Column): Timestamp when the user account was created.
        avatar (Column): URL or path to the user's avatar image.
        refresh_token (Column): Token used for refreshing authentication sessions.
        confirmed (Column): Indicates if the user's email address has been confirmed.
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
