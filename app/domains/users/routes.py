from app.domains.users.schemas import UserCreate
from app.core.deps import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request
from app.domains.users.service import UserService
from app.domains.users.schemas import UserResponse
from app.core.limiter import limiter
from app.core.logging import logger
from app.domains.users.security import require_admin, require_owner_or_admin


router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register new user: {user_data.email}")
    return UserService.create_user(db, user_data)


@router.get("/", response_model=list[UserResponse])
@limiter.limit("100/minute")
def list_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    logger.info("Attempting to list users")
    return UserService.list_users(db, skip, limit)


@router.get("/{user_id}", response_model=UserResponse)
@limiter.limit("60/minute")
def get_user_by_id(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_owner_or_admin),
):
    logger.info(f"Attempting to get user by id: {user_id}")
    return UserService.get_user_by_id(db, user_id)


@router.get("/email/{email}", response_model=UserResponse)
@limiter.limit("60/minute")
def get_user_by_email(
    request: Request,
    email: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    logger.info(f"Attempting to get user by email: {email}")
    return UserService.get_user_by_email(db, email)


@router.get("/username/{username}", response_model=UserResponse)
@limiter.limit("60/minute")
def get_user_by_username(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    logger.info(f"Attempting to get user by username: {username}")
    return UserService.get_user_by_username(db, username)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/hour")
def delete_user(
    request: Request,
    user_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_owner_or_admin),
):
    logger.info(f"Attempting to delete user by id: {user_id}")
    return UserService.delete_user(db, user_id)
