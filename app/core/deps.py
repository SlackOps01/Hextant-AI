from fastapi import Request
from redis.asyncio import Redis
from httpx import AsyncClient
from app.core.database import SessionLocal
from fastapi import Depends, HTTPException, status
from app.core.oauth2 import oauth2_scheme, verify_token, TokenTypes


def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()


def get_redis(request: Request)-> Redis:
    redis_client = request.app.state.redis_client
    return redis_client

def get_http_client(request: Request) -> AsyncClient:
    http_client = request.app.state.http_client
    return http_client


def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credential_exception, expected_token_type=TokenTypes.ACCESS)



