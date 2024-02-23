from src.database.models import User
from sqlalchemy.orm import Session
from libgravatar import Gravatar
from src.schemas.users import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Asynchronously retrieves a user from the database by their email address.

    Args:
        email (str): The email address of the user to be retrieved.
        db (Session): The database session used to execute the query.

    Returns:
        User: An instance of the User model corresponding to the given email address.
              Returns None if no user is found with the given email.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Asynchronously creates a new user in the database, attempting to generate an avatar URL using Gravatar.

    Args:
        body (UserModel): An instance of UserModel containing the new user's information.
        db (Session): The database session used to execute the query.

    Returns:
        User: The newly created User object, including a Gravatar-based avatar URL if successfully generated.

    Raises:
        Exception: Captures and logs any exceptions raised during the Gravatar URL generation process.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Asynchronously updates the refresh token for a specified user in the database.

    Args:
        user (User): The user object whose refresh token is to be updated.
        token (str | None): The new refresh token value. Pass None to remove the token.
        db (Session): The database session used to commit the change.

    Note:
        This function directly modifies the user instance and commits the change to the database.
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Asynchronously marks a user's email as confirmed in the database.

    Args:
        email (str): The email address of the user whose email confirmation status is to be updated.
        db (Session): The database session used to commit the change.

    Note:
        This function relies on `get_user_by_email` to retrieve the user object before updating its 'confirmed' status.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Asynchronously updates the avatar URL for a user identified by their email address.

    Args:
        email (str): The email address of the user whose avatar URL is to be updated.
        url (str): The new avatar URL to be assigned to the user.
        db (Session): The database session used to commit the change.

    Returns:
        User: The user object with the updated avatar URL, if the user is found.

    Note:
        This function retrieves the user object by email before updating the avatar URL.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
