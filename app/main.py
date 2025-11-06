from fastapi import FastAPI
from app.api.main import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

# config = Config('.env')
# app = FastAPI()
# app.add_middleware(SessionMiddleware, secret_key= "a_very_secret_key")
# oauth = OAuth()

# COGNITO_DOMAIN = "https://eu-west-2tolrstzjw.auth.eu-west-2.amazoncognito.com"
# CLIENT_ID = "1j1mb15lir51lhahjvkijt2cgv"
# oauth.register(
#   name='oidc',
#   authority="https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_TolrStzjw",
#   client_id=CLIENT_ID,
#   client_secret=config("CLIENT_SECRET"),
#   server_metadata_url='https://cognito-idp.eu-west-2.amazonaws.com/eu-west-2_TolrStzjw/.well-known/openid-configuration',
#   client_kwargs={'scope': 'email openid phone'}
# )

# # @app.get("/")
# # async def root():
# #   return { "message": "Hello World!"}

# @app.get("/login")
# async def login(request: Request):
#   redirect_uri = request.url_for('auth')
#   return await oauth.oidc.authorize_redirect(request, redirect_uri)

# @app.get("/auth")
# async def auth(request: Request):
#   token = await oauth.oidc.authorize_access_token(request)
#   user = token['userinfo']
#   return dict(user)

# @app.get("/logout")
# async def logout(request: Request):
#   # clear fastapi local session
#   request.session.clear()
#   # cognito_logout_url = (
#   #       f"https://eu-west-2tolrstzjw.auth.eu-west-2.amazoncognito.com/"
#   #       f"logout?client_id={CLIENT_ID}&logout_uri={request.url_for('root')}"
#   #   )
#   logout_url = f"{COGNITO_DOMAIN}/logout?client_id={CLIENT_ID}&logout_uri={request.url_for('root')}"
#   return RedirectResponse(url=logout_url)

# # main.py
# from fastapi import FastAPI, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List

# # Create all tables in the database
# # This will create the 'users' and 'messages' tables if they don't exist
# models.Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(
    title="Duospace Chat API",
    description="Backend API for Duospace chatting application",
    version="1.0.0"
)

# Set all CORS enabled origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)