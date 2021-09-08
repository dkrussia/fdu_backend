import base64
import hashlib
import os
import re
import uuid
from pprint import pprint

from fastapi_mail import MessageSchema
from starlette import status
from datetime import timedelta, datetime

from sqlalchemy.orm.exc import NoResultFound
from fastapi_sqlalchemy import db

from fastapi import APIRouter, Request, HTTPException, Depends, Response

from app.auth.crud.user_token import create_access_token, authenticate_user, get_current_user, create_session, \
    get_password_hash
from app.auth.models import User, UserSession
from app.auth.schema import UserLogin, UserData, RefreshTokenData, GoogleLogin
from app.utils import generate_temporary_password
from core.config import settings
import requests

from core.modules import fm

auth_router = APIRouter()


@auth_router.post("/login")
def login(login_data: UserLogin, request: Request, response: Response):
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO: Проверить сколько у пользователя активных сессий. Если больше 10 - удалять.

    refresh_token = create_session(user, request, request_data=login_data)
    # response.set_cookie("refreshToken", refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES, path='/auth',
    #                      httponly=True, samesite='None')

    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@auth_router.post("/refresh_tokens")
def refresh_tokens(request: Request, refresh_data: RefreshTokenData, response: Response):
    # refresh_token = request.cookies.get('refreshToken')
    refresh_token = refresh_data.refresh_token

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MISSED REFRESH TOKEN",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        session = db.session.query(UserSession).filter_by(refresh_token=refresh_token).one()
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="MISSED SESSION",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.user
    db.session.delete(session)
    db.session.commit()

    if session.fingerprint != refresh_data.fingerprint:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="INVALID_FINGER_PRINT",
            headers={"WWW-Authenticate": "Bearer"},

        )

    if session.expires_in < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOKEN_EXPIRED",
            headers={"WWW-Authenticate": "Bearer"},
        )


    refresh_token = create_session(user, request, request_data=refresh_data)
    response.set_cookie("refreshToken", refresh_token, max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES, path='/auth',
                        httponly=True)
    
    access_token = create_access_token(data={"sub": user.username})

    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@auth_router.post("/logout")
def logout(request: Request):
    refresh_token = request.cookies.get('refreshToken')
    try:
        session = db.session.query(UserSession).filter_by(refresh_token=refresh_token).one()
        db.session.delete(session)
        db.session.commit()
    except NoResultFound:
        pass
    return Response(status_code=204)


@auth_router.get("/user")
def user(current_user: User = Depends(get_current_user)):
    return UserData.from_orm(current_user)


from google.oauth2 import id_token
from google.auth.transport import requests as google_request
# https://developers.google.com/identity/sign-in/web/people
CLIENT_ID = "848887471641-qu2l5auf7hkrfs7b0d7b5md2bn38cq8r.apps.googleusercontent.com"
@auth_router.post("/google")
async def auth_google(google_data: GoogleLogin, request: Request):
    try:
        idinfo = id_token.verify_oauth2_token(google_data.id_token, google_request.Request(), CLIENT_ID)
        user_email = idinfo['email']
        try:
            user = db.session.query(User).filter(User.email == user_email).one()
            access_token = create_access_token(data={"sub": user.username})
            refresh_token = create_session(user, request, request_data=google_data)
            return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
        except NoResultFound:

            temporary_pass = generate_temporary_password()

            new_user = User(username= re.sub(r'[^a-zA-Z0-9]', '', user_email)[:-4],
                            email=user_email,
                            is_active=True,
                            hashed_password=get_password_hash(temporary_pass))

            db.session.add(new_user)
            db.session.commit()

            #### send mail with temporary password
            html = f"""
                        <p>Your login <b>{new_user}</b></p>
                        <p>Hi, you temporary password is --<b>{temporary_pass}</b>--</p>
                    """
            message = MessageSchema(
                subject="FDU login",
                recipients=[user_email],
                body=html,
                subtype="html"
            )
            await fm.send_message(message)
            ####

            access_token = create_access_token(data={"sub": new_user.username})
            refresh_token = create_session(new_user, request, request_data=google_data)
            return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOKEN_INVALID",
        )
