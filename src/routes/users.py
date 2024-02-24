from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.repositories import users as repository_users
from src.services.auth import auth_service
from src.schemas.users import UserDb
from src.load_dotenv import dotenv_load
import os

dotenv_load()


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    Updates the avatar for the currently authenticated user by uploading a new image to Cloudinary.

    This function first configures Cloudinary with credentials stored in environment variables,
    then uploads the provided image file to a specified path using the user's username as a part of the path.
    After uploading, it updates the user's avatar URL in the database with the new image URL.

    Parameters:
        file (UploadFile): The new avatar image to upload.
        current_user (User): The current authenticated user, obtained via dependency.
        db (Session): Database session dependency.

    Returns:
        UserDb: The updated user profile with the new avatar URL.

    Note:
        The function assumes that Cloudinary's environment variables (`CLOUD_NAME`, `API_KEY`, `API_SECRET`) are properly set.
        It also enforces secure HTTPS connections and uses the username to construct a unique public_id for the image in Cloudinary.
    """
    cloudinary.config(
        cloud_name=os.getenv("CLOUD_NAME"),
        api_key=os.getenv("API_KEY"),
        api_secret=os.getenv("API_SECRET"),
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user
