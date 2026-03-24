from redis.asyncio import Redis
from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session
from app.core.oauth2 import TokenData
from app.core.deps import get_current_user, get_redis, get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.core.limiter import limiter
from app.core.logging import logger
from app.domains.auth.service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login")
@limiter.limit("1/second")
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    return AuthService.login(request, response, db, form_data)

@router.post("/logout")
@limiter.limit("1/second")
async def logout(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    return await AuthService.logout(request, response, db, redis)

    

@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    redis: Redis = Depends(get_redis),
    db: Session = Depends(get_db)
):
    return await AuthService.refresh(request, response, db, redis)
