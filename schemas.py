# schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for creating a user
class UserCreate(BaseModel):
    username: str
    email: str

# Schema for returning user data
class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model

# Schema for creating a message
class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    content: str

# Schema for returning message data
class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True