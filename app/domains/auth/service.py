from app.utils.password import hash_password
from app.core.config import CONFIG
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from fastapi import HTTPException, status, Request, Response
from app.core.logging import logger
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.core.oauth2 import create_access_token, create_refresh_token, verify_token, TokenTypes, TokenRequest
from app.domains.users.models import User
from app.domains.auth.models import AuthSessions
from user_agents.parsers import user_agent_parser
from uuid import uuid7
from datetime import datetime, timedelta, timezone
from app.utils.password import verify_password
from sqlalchemy import or_

InvalidCredentialException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, 
    detail="Invalid credentials"
)


class AuthService:
    @staticmethod
    def login(request: Request, response: Response, db: Session, form_data: OAuth2PasswordRequestForm):
        logger.info(f"Attempting login for username/email: {form_data.username}")
        user = db.query(User).filter(
            or_(User.username == form_data.username, User.email == form_data.username)
        ).first()
        if not user:
            logger.warning(f"Login failed: User with email '{form_data.username}' not found.")
            raise InvalidCredentialException
            
        if not verify_password(form_data.password, user.password):
            logger.warning(f"Login failed: Password verification failed for '{form_data.username}'.")
            raise InvalidCredentialException
        

        refresh_token_jti = str(uuid7())

        token_request = TokenRequest(id=user.id, role=user.role)
        access_token = create_access_token(token_request)
        token_request.jti = refresh_token_jti
        refresh_token = create_refresh_token(token_request)

        user_agent_raw = request.headers.get("User-Agent")
        os: dict = user_agent_parser.ParseOS(user_agent_raw)
        device_name: dict = user_agent_parser.ParseDevice(user_agent_raw)
        ip_address = request.client.host


        auth_session = AuthSessions(
            user_id=user.id,
            user_agent=user_agent_raw or "Unknown",
            ip_address=ip_address or "Unknown",
            device_name=device_name["family"],
            device_os=os["family"],
            device_type="Unknown",
            refresh_token_jti=refresh_token_jti,
            session_expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.add(auth_session)
        db.commit()


        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            expires=60*24*7,
            httponly=True,
            samesite="lax",
            secure= CONFIG.SECURE_COOKIES
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }