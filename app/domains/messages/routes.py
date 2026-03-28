from fastapi import APIRouter, Depends, status
from app.core.deps import get_current_user, get_db
from app.core.oauth2 import TokenData
from sqlalchemy.orm import Session
from app.domains.messages.service import MessageService



router = APIRouter(
    prefix="/messages",
    tags=["messages"],
    
)

@router.post("/{conversation_id}", status_code=status.HTTP_201_CREATED)
async def create_message(
    conversation_id: str,
    message: str,
    model_name: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await MessageService.generate_response(
        user_id=current_user.id,
        model_name=model_name,
        conversation_id=conversation_id,
        message=message,
    )
