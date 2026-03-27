from app.core.oauth2 import TokenData
from app.domains.conversations.service import ConversationService
from app.domains.conversations.schemas import ConversationResponse
from app.core.deps import get_db, get_current_user
from app.core.limiter import limiter
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, status, Request


router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post(
    "/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
@limiter.limit("20/minute")
def create_conversation(
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id = current_user.id
    return ConversationService.create_conversation(db, user_id)


@router.get("/", response_model=list[ConversationResponse])
@limiter.limit("60/minute")
def list_conversations(
    request: Request,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id = current_user.id
    return ConversationService.list_conversations(db, user_id)


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/hour")
def delete_conversation(
    request: Request,
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    user_id = current_user.id
    return ConversationService.delete_conversation(db, user_id, conversation_id)
