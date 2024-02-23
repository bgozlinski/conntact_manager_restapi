from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class UserModel(BaseModel):
    """
    A model representing user data for registration purposes.

    Attributes:
        username (str): The username of the user. Must be between 5 and 16 characters.
        email (str): The email address of the user.
        password (str): The password for the user account. Must be between 6 and 24 characters.

    This model is used to validate user registration data, ensuring that usernames and passwords meet the specified criteria.
    """
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=24)


class UserDb(BaseModel):
    """
    A database model representing the stored user data, including metadata like creation time and avatar URL.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        created_at (datetime): The timestamp when the user account was created.
        avatar (str): The URL to the user's avatar image.

    Config:
        orm_mode (bool): Enables ORM mode to facilitate the serialization of ORM objects directly.
    """
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    """
    A response model for user-related operations, encapsulating both the user object and a detail message.

    Attributes:
        user (UserDb): The user object, containing detailed user information.
        detail (str): A message detailing the outcome of the user operation, defaulting to "User successfully created".

    This model is typically used to provide feedback to API consumers following user creation or other operations.
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    A model for authentication tokens returned by the API upon successful authentication.

    Attributes:
        access_token (str): The JWT access token for the session.
        refresh_token (str): The JWT refresh token for generating new access tokens.
        token_type (str): The type of the token, typically "bearer".

    This model specifies the structure of the authentication tokens provided to the client.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    A simple model for requesting operations involving an email address, such as password reset or confirmation emails.

    Attributes:
        email (EmailStr): The email address to be used in the request. Must be a valid email format.

    This model ensures that any email-related request validates the email address format according to RFC 5322 standards.
    """
    email: EmailStr
