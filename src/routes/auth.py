from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas.users import UserModel, UserResponse, TokenModel, RequestEmail
from src.repositories import users as repository_users
from src.services.auth import auth_service

from src.services.email import send_email


router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.

    This endpoint receives user details, creates a new user record in the database, hashes the user's password for security,
    and sends an email confirmation link to the user's email address.

    Parameters:
        body (UserModel): The user details for registration.
        background_tasks (BackgroundTasks): Background tasks for sending email without blocking the response.
        request (Request): The request object to access request details.
        db (Session): The database session dependency.

    Raises:
        HTTPException: 409 Conflict if an account with the provided email already exists.

    Returns:
        A dictionary with details of the created user and a message indicating successful creation and email dispatch.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created. Check your email for confirmation."}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticates a user and provides access and refresh tokens.

    This endpoint validates the user's credentials, checks if the email is confirmed,
    and generates JWT tokens upon successful authentication.

    Parameters:
        body (OAuth2PasswordRequestForm): The login credentials containing the email and password.
        db (Session): The database session dependency.

    Raises:
        HTTPException: 401 Unauthorized if the email is invalid, not confirmed, or the password is incorrect.

    Returns:
        A dictionary with the access token, refresh token, and the token type.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')

    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Refreshes the access token using a refresh token.

    Validates the refresh token and generates new access and refresh tokens.

    Parameters:
        credentials (HTTPAuthorizationCredentials): The refresh token provided by the user.
        db (Session): The database session dependency.

    Raises:
        HTTPException: 401 Unauthorized if the refresh token is invalid.

    Returns:
        A dictionary with the new access token, refresh token, and the token type.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms a user's email address.

    Validates the token from the email link, confirms the user's email in the database if valid.

    Parameters:
        token (str): The token from the confirmation email link.
        db (Session): The database session dependency.

    Raises:
        HTTPException: 400 Bad Request if the token is invalid or the verification process encounters an error.

    Returns:
        A message indicating the outcome of the email confirmation process.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email=email, db=db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification Error')
    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    await repository_users.get_user_by_email(email=email, db=db)
    return {'message': 'Email confirmed'}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    Requests a confirmation email to be sent again.

    For users who haven't confirmed their email, this endpoint allows requesting another confirmation email.

    Parameters:
        body (RequestEmail): The email address to send the confirmation to.
        background_tasks (BackgroundTasks): Background tasks for sending email without blocking the response.
        request (Request): The request object to access request details.
        db (Session): The database session dependency.

    Returns:
        A message indicating that a confirmation email has been sent.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {'message': 'Your email is already confirmed'}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {'message': 'Check your email for confirmation.'}
