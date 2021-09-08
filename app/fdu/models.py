from datetime import datetime

from sqlalchemy.orm import relationship

from app.auth.models import User
from core.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True, index=True)
    lang = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    uuid = Column(String, nullable=False)
    user_id = Column(ForeignKey(User.id))
    user = relationship('User')
