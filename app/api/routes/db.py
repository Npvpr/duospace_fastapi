from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from sqlalchemy import text
import app.models.user as models
import schemas

router = APIRouter()

# Test route - check if API is running
@router.get("/")
def read_root():
    return {"message": "Duospace FastAPI is running! 🚀"}

# Health check route - check database connection
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query to check database connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# Create a new user
@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user instance
    db_user = models.User(username=user.username, email=user.email)
    
    # Add to database and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get the ID from database
    
    return db_user

# Get all users
@router.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Create a new message
@router.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    db_message = models.Message(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# Get messages for a user
@router.get("/messages/{user_id}", response_model=List[schemas.Message])
def read_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | 
        (models.Message.receiver_id == user_id)
    ).all()
    return messages