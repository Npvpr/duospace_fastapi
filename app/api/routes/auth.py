from datetime import datetime, timedelta, timezone
import random, string

import jwt
from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings
from app.core.db import get_db
from app.models import user
import app.utils.auth as auth_utils

# Auth Edge Cases
# 1. User closes tab without confirming email > tries to login again
# - Ask to resend confirmation code
# 2. What if user who already signed up with email/password tries to login via Google/Microsoft OAuth?

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$wagCPXjifgvUFBzq4hqe3w$CYaIb8sB+wtD+Vu/P4uod1+Qof8h+1g7bbDlBID48Rc",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


password_hash = PasswordHash.recommended()


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(email: str, password: str, db: Session = Depends(get_db)):
    user = auth_utils.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Login/Signup flow
# 1. Client sends email to endpoint
# 2. If email already exists, return message to login > enter password
# 3. Check email and password > generate JWT token
# 4. If email does not exist, return message to signup > enter password
# 5. Check password criteria > store email and hashed password > confirm email with code
# (What will happen, if user didn't confirm email and login again?)
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:

    # username is actually email here
    db_user = authenticate_user(form_data.username, form_data.password)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not db_user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not confirmed. Please confirm your email before logging in.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    # print("Generated Access Token:", access_token)
    return Token(access_token=access_token, token_type="bearer")


@router.post("/login-signup")
async def login_signup(email: str, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = auth_utils.get_user_by_email(db, email)
    if db_user:
        return {"message": "Login"}
    else:
        return {"message": "Signup"}


@router.post("/signup")
async def signup(user, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = auth_utils.get_user_by_email(db, email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = get_password_hash(password)

    # Create user but mark as unconfirmed(default)
    db_user = user.User(
        username=email.split("@")[0],
        email=email,
        hashed_password=hashed_password,
    )

    # Add to database and commit
    db.add(db_user)
    db.commit()
    db.refresh(db_user)  # Refresh to get the ID from database

    return JSONResponse(
        status_code=201,
        content={
            "message": "User created successfully. Please confirm your email.",
        },
    )

# Check: Resend confirmation code a million times
@router.get("/send-email-confirmation-code")
async def send_confirmation_code(
    email: str,
    db: Session = Depends(get_db),
):
    db_user = auth_utils.get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if db_user.email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already confirmed"
        )

    # Generate confirmation code
    email_confirmation_code = "".join(random.choices(string.ascii_letters + string.digits, k=6))
    email_confirmation_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Email credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "duospace99@gmail.com"
    sender_password = "your_password_or_app_password"

    # Email content
    subject = "Confirm your email"
    body = f"Your confirmation code is: {email_confirmation_code}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)



    # Send confirmation email
    # auth_utils.send_confirmation_email(email, email_confirmation_code)


@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@router.get("/items")
async def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}
