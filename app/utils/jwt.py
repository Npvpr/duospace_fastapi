from jose import jwt
import requests
from fastapi import HTTPException
from app.core.config import settings

AWS_COGNITO_REGION = settings.AWS_COGNITO_REGION
AWS_COGNITO_USER_POOL_ID = settings.AWS_COGNITO_USER_POOL_ID
AWS_COGNITO_APP_CLIENT_ID = settings.AWS_COGNITO_APP_CLIENT_ID
JWKS_URL = f"https://cognito-idp.{AWS_COGNITO_REGION}.amazonaws.com/{AWS_COGNITO_USER_POOL_ID}/.well-known/jwks.json"

# Fetch Cognito public keys
jwks = requests.get(JWKS_URL).json()

def get_cognito_public_key(kid):
    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    return None

def verify_jwt(token: str):
    header = jwt.get_unverified_header(token)
    key = get_cognito_public_key(header["kid"])
    if not key:
        raise HTTPException(status_code=401, detail="Invalid token header")

    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            audience=AWS_COGNITO_APP_CLIENT_ID,
            issuer=f"https://cognito-idp.{AWS_COGNITO_REGION}.amazonaws.com/{AWS_COGNITO_USER_POOL_ID}",
        )
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
