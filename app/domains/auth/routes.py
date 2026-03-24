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



