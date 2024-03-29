from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.load_dotenv import dotenv_load
import os

dotenv_load()

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{os.getenv('USERNAME_DB')}:{os.getenv('USERNAME_PASSWORD')}@{os.getenv('HOST_DB')}:{os.getenv('PORT_DB')}/{os.getenv('NAME_DB')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Generator function that provides a database session.

    This function is intended for use with dependency injection in web applications,
    ensuring that a new database session is created for each request and properly closed after use.

    Yields:
        SessionLocal: An instance of a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
