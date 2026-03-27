from fastapi import HTTPException, status
from app.domains.tiers.models import Tiers
from app.domains.tiers.schemas import TierCreate, TierResponse, TierUpdate
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


TierConflictException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Tier with this name already exists",
)

TierNotFoundException = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Tier not found",
)


class TierService:
    @staticmethod
    def create_tier(db: Session, tier_data: TierCreate) -> TierResponse:
        tier = Tiers(**tier_data.model_dump(mode="json"))
        db.add(tier)
        try:
            db.commit()
            db.refresh(tier)
        except IntegrityError:
            db.rollback()
            raise TierConflictException
        return TierResponse.model_validate(tier)

    @staticmethod
    def list_tiers(db: Session) -> list[TierResponse]:
        tiers = db.query(Tiers).all()
        return [TierResponse.model_validate(tier) for tier in tiers]

    @staticmethod
    def get_tier_by_id(db: Session, tier_id: str) -> TierResponse:
        tier = db.query(Tiers).filter(Tiers.id == tier_id).first()
        if not tier:
            raise TierNotFoundException
        return TierResponse.model_validate(tier)

    @staticmethod
    def update_tier(db: Session, tier_id: str, tier_data: TierUpdate) -> TierResponse:
        tier = db.query(Tiers).filter(Tiers.id == tier_id).first()
        if not tier:
            raise TierNotFoundException

        update_data = tier_data.model_dump(exclude_unset=True, mode="json")
        for key, value in update_data.items():
            setattr(tier, key, value)

        try:
            db.commit()
            db.refresh(tier)
        except IntegrityError:
            db.rollback()
            raise TierConflictException

        return TierResponse.model_validate(tier)

    @staticmethod
    def delete_tier(db: Session, tier_id: str) -> None:
        tier = db.query(Tiers).filter(Tiers.id == tier_id).first()
        if not tier:
            raise TierNotFoundException
        db.delete(tier)
        db.commit()
