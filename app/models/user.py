from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.db import Base


class User(Base):
    __tablename__ = "users"  # This will be the table name in PostgreSQL

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    email_confirmed = Column(Boolean, default=False)
    email_confirmation_code = Column(String(6), nullable=True, default=None)
    email_confirmation_expiry = Column(DateTime(timezone=True), nullable=True, default=None)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now()
    )  # Auto-set timestamp


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, index=True)
    receiver_id = Column(Integer, index=True)
    content = Column(Text)  # For long text messages
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
