from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repositories import users as repository_users


class Auth:
    """
    Provides authentication and authorization utilities for FastAPI applications.

    This class uses the PassLib library to hash and verify passwords securely, and the python-jose library
    to encode, decode, and verify JWT tokens.

    Attributes:
        pwd_context (CryptContext): The PassLib context for hashing passwords using bcrypt.
        SECRET_KEY (str): The secret key for encoding JWT tokens. Should be kept secret in production.
        ALGORITHM (str): The algorithm used for JWT encoding and decoding.
        oauth2_scheme (OAuth2PasswordBearer): The OAuth2 scheme for bearer tokens.

    Methods:
        verify_password(plain_password, hashed_password): Verifies a password against a hashed version.
        get_password_hash(password): Hashes a password.
        create_access_token(data, expires_delta): Creates a JWT access token.
        create_refresh_token(data, expires_delta): Creates a JWT refresh token.
        decode_refresh_token(refresh_token): Decodes a JWT refresh token.
        get_current_user(token, db): Retrieves the current user based on a JWT token.
        create_email_token(data): Creates a token for email actions like verification.
        get_email_from_token(token): Extracts and returns the email from a JWT token.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies a password against its hashed version.

        Parameters:
            plain_password (str): The plaintext password to verify.
            hashed_password (str): The hashed password to verify against.

        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes a password.

        Parameters:
            password (str): The plaintext password to hash.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a JWT access token with a specified expiration time.

        Parameters:
            data (dict): The data to encode into the token, typically containing the user identifier.
            expires_delta (Optional[float]): The number of seconds until the token expires. Defaults to 15 minutes.

        Returns:
            str: The encoded JWT access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Creates a JWT refresh token with a specified expiration time.

        Parameters:
            data (dict): The data to encode into the token, typically containing the user identifier.
            expires_delta (Optional[float]): The number of seconds until the token expires. Defaults to 7 days.

        Returns:
            str: The encoded JWT refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decodes a JWT refresh token, verifying its validity and scope.

        Parameters:
            refresh_token (str): The JWT refresh token to decode.

        Returns:
            str: The email of the user to whom the token was issued.

        Raises:
            HTTPException: If the token is invalid or has an incorrect scope.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Retrieves the current user based on a JWT access token.

        Parameters:
            token (str): The JWT access token.
            db (Session): The database session.

        Returns:
            User: The user object corresponding to the token's subject.

        Raises:
            HTTPException: If the token is invalid or the user does not exist.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict):
        """
        Creates a token for email-related actions (e.g., verification).

        Parameters:
            data (dict): The data to encode into the token, typically containing the user's email.

        Returns:
            str: The encoded JWT token for email actions.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({
            'iat': datetime.utcnow(),
            'exp': expire
        })

        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

        return token

    async def get_email_from_token(self, token: str):
        """
        Extracts and returns the email address from a JWT token intended for email actions.

        Parameters:
            token (str): The JWT token from which to extract the email.

        Returns:
            str: The email address encoded in the token.

        Raises:
            HTTPException: If the token is invalid or improperly formatted.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")


auth_service = Auth()
