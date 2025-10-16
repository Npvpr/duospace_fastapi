from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from db import engine, get_db
import models
import schemas

config = Config('.env')
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key= "a_very_secret_key")
oauth = OAuth()

COGNITO_DOMAIN = "https://eu-west-2tolrstzjw.auth.eu-west-2.amazoncognito.com"
CLIENT_ID = "1j1mb15lir51lhahjvkijt2cgv"
oauth.register(
  name='oidc',
  authority="https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_TolrStzjw",
  client_id=CLIENT_ID,
  client_secret=config("CLIENT_SECRET"),
  server_metadata_url='https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_TolrStzjw/.well-known/openid-configuration',
  client_kwargs={'scope': 'email openid phone'}
)

# @app.get("/")
# async def root():
#   return { "message": "Hello World!"}

@app.get("/login")
async def login(request: Request):
  redirect_uri = request.url_for('auth')
  return await oauth.oidc.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
  token = await oauth.oidc.authorize_access_token(request)
  user = token['userinfo']
  return dict(user)

@app.get("/logout")
async def logout(request: Request):
  # clear fastapi local session
  request.session.clear()
  # cognito_logout_url = (
  #       f"https://eu-west-2tolrstzjw.auth.eu-west-2.amazoncognito.com/"
  #       f"logout?client_id={CLIENT_ID}&logout_uri={request.url_for('root')}"
  #   )
  logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri={request.url_for('root')}"
  return RedirectResponse(url=logout_url)

# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Create all tables in the database
# This will create the 'users' and 'messages' tables if they don't exist
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(
    title="Duospace Chat API",
    description="Backend API for Duospace chatting application",
    version="1.0.0"
)

# Test route - check if API is running
@app.get("/")
def read_root():
    return {"message": "Duospace FastAPI is running! 🚀"}

# Health check route - check database connection
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query to check database connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

# Create a new user
@app.post("/users/", response_model=schemas.User)
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
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

# Create a new message
@app.post("/messages/", response_model=schemas.Message)
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
@app.get("/messages/{user_id}", response_model=List[schemas.Message])
def read_messages(user_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | 
        (models.Message.receiver_id == user_id)
    ).all()
    return messages