from fastapi import HTTPException, status
from app.domains.conversations.schemas import ConversationUpdate
from sqlalchemy.orm import Session
from app.domains.conversations.schemas import ConversationResponse, ConversationUpdate
from app.domains.conversations.models import Conversations
from redis.asyncio import Redis
import json

class ConversationNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

class ConversationService:
    @staticmethod
    async def create_conversation(db: Session, user_id: str, redis: Redis) -> ConversationResponse:
        conversation = Conversations(
            user_id=user_id,
            title="New Conversation",
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        cache_key = f"conversations:{user_id}"
        await redis.delete(cache_key)
        return conversation

    @staticmethod
    async def list_conversations(db: Session, user_id: str, redis: Redis) -> list[ConversationResponse]:
        cache_key = f"conversations:{user_id}"
        conversations = await redis.get(cache_key)
        if conversations:
            return [ConversationResponse(**item) for item in json.loads(conversations)]
        conversations = db.query(Conversations).filter(Conversations.user_id == user_id).all()
        serialized_items = [ConversationResponse.model_validate(item) for item in conversations]
        dict_items = [item.model_dump() for item in serialized_items]
        await redis.setex(cache_key, 60*60, json.dumps(dict_items, default=str))
        return conversations

    @staticmethod
    async def update_conversation(db: Session, data: ConversationUpdate, user_id: str, conversation_id: str, redis: Redis) -> ConversationResponse:
        conversation = db.query(Conversations).filter(Conversations.id==conversation_id, Conversations.user_id == user_id).first()
        if not conversation:
            raise ConversationNotFoundException()
        conversation.title = data.title
        db.commit()
        db.refresh(conversation)
        cache_key = f"conversations:{user_id}"
        await redis.delete(cache_key)
        return conversation

    @staticmethod
    async def delete_conversation(db: Session, user_id: str, conversation_id: str, redis: Redis):
        conversation = db.query(Conversations).filter(Conversations.id==conversation_id, Conversations.user_id == user_id).first()
        if not conversation:
            raise ConversationNotFoundException()

        db.delete(conversation)
        db.commit()
        cache_key = f"conversations:{user_id}"
        await redis.delete(cache_key)

        return {
            "status": "deleted"
        }