from sqlalchemy.orm import Session
from app.domains.conversations.schemas import ConversationCreate, ConversationResponse
from app.core.deps import get_db
from app.domains.conversations.models import Conversations

class ConversationService:
    
    @staticmethod
    def create_conversation(db: Session, user_id: str, data: ConversationCreate) -> ConversationResponse:
        conversation = Conversations(
            user_id=user_id,
            title=data.title,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation