from app.core.oauth2 import TokenData
from app.domains.conversations.service import ConversationService
from app.domains.conversations.schemas import ConversationCreate, ConversationResponse
from app.core.deps import get_db, get_current_user
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    user_id = current_user.id
    return ConversationService.create_conversation(db, user_id, data)