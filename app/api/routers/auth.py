from fastapi import APIRouter, HTTPException, Header
from fastapi.params import Depends

from app.utils.jwt import verify_jwt

router = APIRouter()

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    payload = verify_jwt(token)
    return payload

@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return {
        "sub": user["sub"],
        "email": user.get("email"),
    }