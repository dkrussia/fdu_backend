import re
from fastapi_sqlalchemy import db
from sqlalchemy.exc import NoResultFound
from app.auth.models import User
from app.utils import BaseSchema
from pydantic import EmailStr, validator, Field


class RegisterForm(BaseSchema):
    username: str = Field(min_length=2)
    password: str = Field(min_length=2)
    email: EmailStr

    @validator('username')
    def name_validator(cls, v):
        r_result = re.findall('^[a-zA-Z]+$', v)
        if not r_result:
            raise ValueError('Имя пользователя должно содержать только '
                             'латинские символы')
        try:
            db.session.query(User).filter(User.username == v).one()
            raise ValueError('Пользователь с таким именем уже существует')
        except NoResultFound:
            pass
        return v

    @validator('password')
    def password_validator(cls, v):
        if (len(v) < 5):
            raise ValueError('Пароль должен быть длинее 4 симовлов')
        return v

    @validator('email')
    def email_validator(cls, v):
        try:
            db.session.query(User).filter(User.email == v).one()
            raise ValueError('Пользователь с таким email уже существует')
        except NoResultFound:
            pass
        return v


class ChangePasswordForm(BaseSchema):
    current_password: str = Field(type='string')
    new_password: str = Field(type='string')

    @validator('new_password')
    def new_password_validator(cls, v, values):
        if (len(v) < 5):
            raise ValueError('Пароль должен быть длинее 4 симовлов')
        return v

    @validator('current_password')
    def current_password_validator(cls, v):
        return v


class ChangeUsernameForm(BaseSchema):
    username: str = Field(type='Имя аккаунта')

    @validator('username')
    def name_validator(cls, v):
        r_result = re.findall('^[a-zA-Z]+$', v)
        if not r_result:
            raise ValueError('Имя пользователя должно содержать только '
                             'латинские символы')
        try:
            db.session.query(User).filter(User.username == v).one()
            raise ValueError('Пользователь с таким именем уже существует')
        except NoResultFound:
            pass
        return v


class ResetPasswordForm(BaseSchema):
    email: EmailStr = Field(type='Почта')

    @validator('email')
    def email_validator(cls, v):
        try:
            db.session.query(User).filter(User.email == v).one()
        except NoResultFound:
            raise ValueError('Пользователь с таким email не существует')
        return v
