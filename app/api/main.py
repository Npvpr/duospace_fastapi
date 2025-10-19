from fastapi import APIRouter
from app.api.routers import auth, db

api_router = APIRouter()
api_router.include_router(db.router, prefix="/db", tags=["database"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
