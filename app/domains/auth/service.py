from app.core.tokens import revoke_tokens, is_token_revoked

from app.core.config import CONFIG
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from fastapi import HTTPException, status, Request, Response
from app.core.logging import logger
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.core.oauth2 import (
    create_access_token,
    create_refresh_token,
    verify_token,
    TokenTypes,
    TokenRequest,
)
from app.domains.users.models import User
from app.domains.auth.models import AuthSessions
from user_agents.parsers import user_agent_parser
from uuid import uuid7
from datetime import datetime, timedelta, timezone
from app.utils.password import verify_password
from sqlalchemy import or_
from fastapi.concurrency import run_in_threadpool  # For blocking async code


class InvalidCredentialException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

class RevokedSessionException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session has been revoked")


def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=60 * 60 * 24 * 7,
        httponly=True,
        samesite="lax",
        path="/",
        secure=CONFIG.SECURE_COOKIES,
    )


class AuthService:
    @staticmethod
    def login(
        request: Request,
        response: Response,
        db: Session,
        form_data: OAuth2PasswordRequestForm,
    ):
        logger.info(f"Attempting login for username/email: {form_data.username}")
        user = (
            db.query(User)
            .filter(
                or_(
                    User.username == form_data.username,
                    User.email == form_data.username,
                )
            )
            .first()
        )
        if not user:
            logger.warning(
                f"Login failed: User with email '{form_data.username}' not found."
            )
            raise InvalidCredentialException()

        if not verify_password(form_data.password, user.password):
            logger.warning(
                f"Login failed: Password verification failed for '{form_data.username}'."
            )
            raise InvalidCredentialException()

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
            device_name=device_name.get("family", "unknown"),
            device_os=os.get("family", "unknown"),
            device_type="Unknown",
            refresh_token_jti=refresh_token_jti,
            session_expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(auth_session)
        db.commit()

        set_refresh_cookie(response, refresh_token)

        return {"access_token": access_token, "token_type": "bearer"}

    @staticmethod
    async def logout(request: Request, response: Response, db: Session, redis: Redis):
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            raise InvalidCredentialException()

        token_data = verify_token(
            refresh_token, InvalidCredentialException, TokenTypes.REFRESH
        )
        auth_session = await run_in_threadpool(
            lambda: db.query(AuthSessions)
            .filter(AuthSessions.refresh_token_jti == token_data.jti)
            .first()
        )
        if not auth_session:
            raise InvalidCredentialException()
        auth_session.is_revoked = True
        await run_in_threadpool(lambda: db.commit())

        if await is_token_revoked(redis, token_data.jti):
            raise RevokedSessionException()

        await revoke_tokens(redis, token_data.jti, token_data.exp)
        response.delete_cookie(
            key="refresh_token",
            httponly=True,
            samesite="lax",
            path="/",
            secure=CONFIG.SECURE_COOKIES,
        )

        return {"status": "revoked"}

    @staticmethod
    async def refresh(request: Request, response: Response, db: Session, redis: Redis):
        token = request.cookies.get("refresh_token")
        if not token:
            raise InvalidCredentialException()

        token_data = verify_token(token, InvalidCredentialException, TokenTypes.REFRESH)

        auth_session = await run_in_threadpool(
            lambda: db.query(AuthSessions)
            .filter(AuthSessions.refresh_token_jti == token_data.jti)
            .first()
        )
        if not auth_session or auth_session.is_revoked:
            raise InvalidCredentialException()

        if await is_token_revoked(redis, token_data.jti):
            raise RevokedSessionException()

        await revoke_tokens(redis, token_data.jti, token_data.exp)

        refresh_token_jti = str(uuid7())

        refresh_token = create_refresh_token(
            TokenRequest(id=token_data.id, role=token_data.role, jti=refresh_token_jti)
        )
        access_token = create_access_token(
            TokenRequest(id=token_data.id, role=token_data.role)
        )

        auth_session.refresh_token_jti = refresh_token_jti

        await run_in_threadpool(lambda: db.commit())

        set_refresh_cookie(response, refresh_token)

        return {"access_token": access_token, "token_type": "bearer"}
