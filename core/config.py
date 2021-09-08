import os

from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings, Field, EmailStr
import logging

logger = logging.getLogger('uvicorn')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER_MODE = os.getenv("SERVER_MODE", "local")
logger.warning(f'SERVER MODE SET ---{SERVER_MODE}---')

MAIL_TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'emails')


class Settings(BaseSettings):
    app_name: str = "supercw"

    PORT: int
    HOST: str
    RELOAD_SERVER: bool = Field(default=False)
    ORIGINS: str

    DATABASE_URL: str
    BASE_DIR: str = BASE_DIR
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str

    class Config:
        env_file = f"{BASE_DIR}/.env.{SERVER_MODE}"
        env_file_encoding = 'utf-8'


settings = Settings()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=EmailStr('noreply@supercw.ru'),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.mail.ru",
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    MAIL_DEBUG=1,
    TEMPLATE_FOLDER=MAIL_TEMPLATE_FOLDER
)
