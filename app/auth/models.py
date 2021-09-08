from datetime import datetime

from sqlalchemy.orm import relationship

from core.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, index=True)
    email = Column(String(100), nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)



class UserSession(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(ForeignKey(User.id))
    refresh_token = Column(String, nullable=False)
    ua = Column(String, nullable=False)
    fingerprint = Column(String, nullable=False)
    ip = Column(String, nullable=False)
    expires_in = Column(DateTime, nullable=False)
    created_in = Column(DateTime, default=datetime.now)

    user = relationship('User')
