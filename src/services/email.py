from fastapi_mail import ConnectionConfig, MessageSchema, MessageType, FastMail
from pydantic import EmailStr
from pathlib import Path
from src.services.auth import auth_service
from fastapi_mail.errors import ConnectionErrors
from src.load_dotenv import dotenv_load
import os

dotenv_load()

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=os.getenv("MAIL_PORT"),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({'sub': email})
        message = MessageSchema(
            subject='Confirm your email',
            recipients=[email],
            template_body={
                'host': host,
                'username': username,
                'token': token_verification
            },
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message=message, template_name='email_template.html')

    except ConnectionErrors as e:
        print(e)
