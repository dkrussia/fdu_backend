from fastapi import APIRouter, Depends, HTTPException
from fastapi_mail import MessageSchema
from starlette import status
from app.auth.crud.user_token import get_password_hash, get_current_user, verify_password, get_user_by_email
from app.userprofile.models import ResetPasswordRequest
from app.userprofile.schema import RegisterForm, ChangePasswordForm, ChangeUsernameForm, ResetPasswordForm
from app.auth.models import User
from fastapi_sqlalchemy import db

from app.utils import generate_temporary_password
from core.modules import fm

userprofile_router = APIRouter()


@userprofile_router.post('/registration')
async def registration(reg_data: RegisterForm):
    new_user = User(username=reg_data.username,
                    email=reg_data.email,
                    hashed_password=get_password_hash(reg_data.password),
                    is_active=True)
    db.session.add(new_user)
    db.session.commit()

    html = """<p>Welcome from supercw</p>"""
    message = MessageSchema(
        subject="Hello, hi!",
        recipients=[reg_data.email],
        body=html,
        subtype="html"
    )
    await fm.send_message(message)

    return {'result': True, 'message': 'Вы зарегистрированы.'}


@userprofile_router.post('/change_password')
def change_password(change_username_data: ChangePasswordForm, user=Depends(get_current_user)):
    if not verify_password(change_username_data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={'errors': {'current_password': 'Invalid password'}},
            headers={"WWW-Authenticate": "Bearer"},
        )
    user.hashed_password = get_password_hash(change_username_data.new_password)
    db.session.add(user)
    db.session.commit()
    return {'result': True}


@userprofile_router.get('/change_password/form')
def change_password_form():
    r = {}
    r["headers"] = ChangePasswordForm.get_headers()
    r["result"] = True

    return r


@userprofile_router.get('/change_username/form')
def change_password_form(user=Depends(get_current_user)):
    r = {}
    r["headers"] = ChangeUsernameForm.get_headers()
    r["result"] = True
    r['item'] = {
        "username": user.username
    }
    return r


@userprofile_router.post('/change_username')
def change_password(change_username_data: ChangeUsernameForm, user=Depends(get_current_user)):
    user.username = change_username_data.username
    db.session.add(user)
    db.session.commit()
    return {'result': True}


@userprofile_router.post('/reset_password')
async def reset_password(reset_password_data: ResetPasswordForm):
    temporary_password = generate_temporary_password()
    user = get_user_by_email(reset_password_data.email)

    hashed_password = get_password_hash(temporary_password)
    user.hashed_password = hashed_password

    password_request = ResetPasswordRequest(
        user_id=user.id,
        temporary_password=hashed_password
    )

    db.session.add(password_request)
    db.session.add(user)

    db.session.commit()

    html = f"""<p>Hi, you temporary password is <b>{temporary_password}</b>"""
    message = MessageSchema(
        subject="Welcome to superCW",
        recipients=[reset_password_data.email],
        body=html,
        subtype="html"
    )

    await fm.send_message(message)

    return {'result': True,
            'message': 'Временный пароль отправлен Вам на почту.'
                       '\nИзмените его при первом входе в систему.'}
