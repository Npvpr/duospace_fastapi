from datetime import datetime, timedelta
import random
import string

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models import user

def get_user_by_email(db, email: str):
    return db.query(user.User).filter(user.User.email == email).first()

def generate_confirmation_code(length=6):
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def send_confirmation_email(to_email: str, code: str):
    # Email credentials
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "duospace99@gmail.com"
    sender_password = "your_password_or_app_password"

    # Email content
    subject = "Confirm your email"
    body = f"Your confirmation code is: {code}"

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print(f"Confirmation code sent to {to_email}")
