from app.domains.tiers.service import TierService
from app.domains.tiers.schemas import TierCreate, TierResponse, TierUpdate
from app.domains.users.security import require_admin
from app.core.deps import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends

router = APIRouter(prefix="/tiers", tags=["Tiers"])


@router.post("/", response_model=TierResponse, status_code=status.HTTP_201_CREATED)
def create_tier(
    tier_data: TierCreate, db: Session = Depends(get_db), _=Depends(require_admin)
):
    return TierService.create_tier(db, tier_data)


@router.get("/", response_model=list[TierResponse], status_code=status.HTTP_200_OK)
def list_tiers(db: Session = Depends(get_db)):
    return TierService.list_tiers(db)


@router.get("/{tier_id}", response_model=TierResponse, status_code=status.HTTP_200_OK)
def get_tier_by_id(tier_id: str, db: Session = Depends(get_db)):
    return TierService.get_tier_by_id(db, tier_id)


@router.patch(
    "/{tier_id}", response_model=TierResponse, status_code=status.HTTP_202_ACCEPTED
)
def update_tier(
    tier_id: str,
    tier_data: TierUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    return TierService.update_tier(db, tier_id, tier_data)


@router.delete("/{tier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tier(tier_id: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    TierService.delete_tier(db, tier_id)
    return
