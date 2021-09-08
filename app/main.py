import logging
from typing import List

from fastapi import FastAPI
from fastapi_mail import FastMail, MessageSchema
from pydantic import BaseModel, EmailStr
from starlette.middleware.cors import CORSMiddleware
from app.auth.endpoints import auth_router
from fastapi_sqlalchemy import DBSessionMiddleware

from app.fdu.endpoints import fdu_router
from core.config import settings
from app.i18n import i18nMiiddleware
from app.userprofile.endpoints import userprofile_router
from core.config import mail_conf
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger('custom')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class EmailSchema(BaseModel):
    emails: List[EmailStr]


def create_app():
    app = FastAPI()
    app.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    app.add_middleware(i18nMiiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ORIGINS.split(','),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router, prefix="/auth")
    app.include_router(userprofile_router, prefix="/userprofile")
    app.include_router(fdu_router, prefix="/fdu")

    app.mount("/static", StaticFiles(directory="logs"), name="static")

    return app


app = create_app()


@app.get("/ping")
async def ping():
    html = """<p>Hello from supercw</p>"""
    message = MessageSchema(
        subject="Test Massage",
        recipients=[EmailStr('ex-2k@yandex.ru')],
        body=html,
        subtype="html"
    )
    fm = FastMail(mail_conf)
    await fm.send_message(message, template_name='success_registration.html')
    return {"pong": True}
