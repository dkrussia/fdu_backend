from datetime import datetime

from sqlalchemy.orm import relationship

from app.auth.models import User
from core.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime


class ResetPasswordRequest(Base):
    __tablename__ = "reset_passwords"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey(User.id), nullable=False)
    created_in = Column(DateTime, default=datetime.now, nullable=False)
    temporary_password = Column(String, nullable=False)

    user = relationship('User')
