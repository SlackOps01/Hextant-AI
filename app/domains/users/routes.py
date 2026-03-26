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


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("1/second")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to register new user: {user_data.email}")
    return UserService.create_user(db, user_data)

@router.get("/", response_model=list[UserResponse])
@limiter.limit("10/minute")
def list_users(
    request: Request, 
    skip: int = 0, 
    limit: int = 100, 
    db: Session=Depends(get_db),
    _=Depends(require_admin)
):
    logger.info("Attempting to list users")
    return UserService.list_users(db, skip, limit)


@router.get("/{id}", response_model=UserResponse)
@limiter.limit("1/second")
def get_user_by_id(
    request: Request, 
    id: str, 
    db: Session=Depends(get_db), 
    _=Depends(require_owner_or_admin)
):
    logger.info(f"Attempting to get user by id: {id}")
    return UserService.get_user_by_id(db, id)

@router.get("/email/{email}", response_model=UserResponse)
@limiter.limit("1/second")
def get_user_by_email(
    request: Request, 
    email: str, 
    db: Session=Depends(get_db),
    _=Depends(require_owner_or_admin)
):

    logger.info(f"Attempting to get user by email: {email}")
    return UserService.get_user_by_email(db, email)

@router.get("/username/{username}", response_model=UserResponse)
@limiter.limit("1/second")
def get_user_by_username(
    request: Request, 
    username: str, 
    db: Session=Depends(get_db),
    _=Depends(require_owner_or_admin)
):
    logger.info(f"Attempting to get user by username: {username}")
    return UserService.get_user_by_username(db, username)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    request: Request,
    id: str, 
    db: Session = Depends(get_db),
    _=Depends(require_owner_or_admin)
):
    logger.info(f"Attempting to delete user by id: {id}")
    return UserService.delete_user(db, id)
