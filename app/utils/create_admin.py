from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.logging import logger
from app.core.config import CONFIG
from app.domains.users.models import User
from app.shared.enums import Role
from app.utils.password import hash_password


def create_admin_user() -> None:
    db: Session = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == Role.ADMIN.value).first()
        if existing_admin:
            logger.info("Admin user already exists")
            return

        hashed_password = hash_password(CONFIG.ADMIN_PASSWORD)
        admin_user = User(
            username=CONFIG.ADMIN_USERNAME,
            email=CONFIG.ADMIN_EMAIL,
            password=hashed_password,
            role=Role.ADMIN,
        )
        db.add(admin_user)
        db.commit()
        logger.info(f"Admin user created: {CONFIG.ADMIN_USERNAME}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create admin user: {e}")
    finally:
        db.close()
