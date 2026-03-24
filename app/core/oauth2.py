from pydantic import BaseModel, ValidationError
from jose import jwt, JWTError
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.core.config import CONFIG
from datetime import datetime, timedelta, timezone
from uuid import uuid7
from enum import Enum
from app.shared.enums import Role
from typing import Optional


class TokenTypes(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class TokenRequest(BaseModel):
    id: str
    role: Role
    exp: datetime

class TokenData(BaseModel):
    id: str
    role: Role
    exp: datetime
    jti: Optional[str]


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict) -> str:
    payload = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(minutes=CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload.update({
        "exp": exp,
        "token_type": TokenTypes.ACCESS.value
    })
    
    return jwt.encode(payload, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(days=CONFIG.REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload.update({
        "exp": exp,
        "jti": str(uuid7()),
        "token_type": TokenTypes.REFRESH.value
    })
    
    return jwt.encode(payload, CONFIG.SECRET_KEY, algorithm=CONFIG.ALGORITHM)

def verify_token(token: str, credentials_exception, expected_token_type: TokenTypes) -> TokenData:
    try:
        # 1. Decode the token (jose automatically verifies expiration 'exp' here!)
        payload = jwt.decode(token, CONFIG.SECRET_KEY, algorithms=[CONFIG.ALGORITHM])

        # 2. Enforce the token type immediately
        if payload.get("token_type") != expected_token_type.value:
            raise credentials_exception

        # 3. Let Pydantic validate the payload
        # If 'id', 'role', or 'exp' are missing, Pydantic raises a ValidationError
        token_data = TokenData(**payload)

        # 4. Enforce the JTI requirement for refresh tokens
        if expected_token_type == TokenTypes.REFRESH and not token_data.jti:
            raise credentials_exception

        return token_data

    except (JWTError, ValidationError):
        # Catch both JWT parsing errors AND Pydantic validation errors
        raise credentials_exception






    



