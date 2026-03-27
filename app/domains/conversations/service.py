from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.domains.conversations.schemas import ConversationResponse, ConversationUpdate
from app.domains.conversations.models import Conversations


ConversationNotFoundException = HTTPException(
    detail="Conversation not found", status_code=status.HTTP_404_NOT_FOUND
)


class ConversationService:
    @staticmethod
    def create_conversation(db: Session, user_id: str) -> ConversationResponse:
        conversation = Conversations(
            user_id=user_id,
            title="New Conversation",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def list_conversations(db: Session, user_id: str) -> list[ConversationResponse]:
        conversations = (
            db.query(Conversations).filter(Conversations.user_id == user_id).all()
        )
        return conversations

    @staticmethod
    def update_conversation(
        db: Session, data: ConversationUpdate, user_id: str, conversation_id: str
    ) -> ConversationResponse:
        conversation = (
            db.query(Conversations)
            .filter(
                Conversations.id == conversation_id, Conversations.user_id == user_id
            )
            .first()
        )
        if not conversation:
            raise ConversationNotFoundException
        conversation.title = data.title
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def delete_conversation(db: Session, user_id: str, conversation_id: str):
        conversation = (
            db.query(Conversations)
            .filter(
                Conversations.id == conversation_id, Conversations.user_id == user_id
            )
            .first()
        )
        if not conversation:
            raise ConversationNotFoundException

        db.delete(conversation)
        db.commit()

        return {"status": "deleted"}
