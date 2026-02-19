import datetime as _datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class UserModel(Base):
    __tablename__ = "fd_users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())

class TokenBlacklistModel(Base):
    __tablename__ = "blacklist"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
