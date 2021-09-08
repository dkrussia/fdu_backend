from fastapi_mail import FastMail
from core.config import mail_conf

fm = FastMail(mail_conf)