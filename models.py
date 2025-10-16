from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from db import Base

class User(Base):
    __tablename__ = "users"  # This will be the table name in PostgreSQL
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto-set timestamp

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, index=True)
    receiver_id = Column(Integer, index=True)
    content = Column(Text)  # For long text messages
    timestamp = Column(DateTime(timezone=True), server_default=func.now())