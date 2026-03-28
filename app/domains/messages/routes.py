from fastapi import APIRouter, Depends, status
from app.core.deps import get_current_user, get_db
from app.core.oauth2 import TokenData
from sqlalchemy.orm import Session
from app.domains.messages.service import MessageService
from app.domains.messages.schemas import MessageCreate


router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    
)

@router.post("/{conversation_id}", status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
    data: MessageCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await MessageService.generate_response(
        conversation_id=conversation_id,
        data=data,
        db=db,
        current_user=current_user
    )
