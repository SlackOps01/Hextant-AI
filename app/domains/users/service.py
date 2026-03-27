from fastapi import HTTPException, status
from app.domains.users.schemas import UserUpdate
from app.domains.users.schemas import UserResponse
from app.domains.users.schemas import UserCreate
from sqlalchemy.orm import Session
from app.domains.users.models import User
from app.utils.password import hash_password


UserNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
)

UserActionForbiddenException = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="Action forbidden!"
)


class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: str):
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundException
        return user

    @staticmethod
    def get_user_by_username(db: Session, username: str):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise UserNotFoundException
        return user

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100):
        # No auth logic here anymore!
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def delete_user(db: Session, user_id: str):
        # No auth logic here anymore!
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException
        db.delete(user)
        db.commit()
        return {
            "status": "success",
        }

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> UserResponse:
        # Hash the password on the Pydantic object first
        user_data.password = hash_password(user_data.password)

        # Dump to dict. mode="json" ensures URLs/UUIDs are converted to strings for SQLAlchemy
        user_dict = user_data.model_dump(mode="json")

        user = User(**user_dict)
        db.add(user)
        db.commit()
        db.refresh(user)

        # Use the modern Pydantic V2 method
        return UserResponse.model_validate(user)

    @staticmethod
    def update_user(db: Session, user_id: str, user_data: UserUpdate) -> UserResponse:
        # No auth logic here anymore!
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise UserNotFoundException

        update_dict = user_data.model_dump(exclude_unset=True, mode="json")

        # Safely check the dictionary for a password update
        if "password" in update_dict:
            update_dict["password"] = hash_password(update_dict["password"])

        # Apply the updates to the SQLAlchemy model
        for key, value in update_dict.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)  # Make sure we get the latest updated_at timestamp!

        # Actually return the response!
        return UserResponse.model_validate(user)
