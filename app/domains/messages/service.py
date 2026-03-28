from pydantic_ai import TextPart
from pydantic_ai import ModelResponse
from pydantic_ai import ModelRequest
from app.domains.messages.models import MessageRole
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from app.core.config import CONFIG
from pydantic_ai.providers.openrouter import OpenRouterProvider
from app.domains.messages.schemas import MessageCreate, MessageResponse
from app.domains.llm_models.models import LanguageModels
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.domains.messages.models import Messages, MessageType
from pydantic_ai.messages import ModelMessage, UserPromptPart
from app.domains.conversations.models import Conversations
from app.core.oauth2 import TokenData


def _build_message_history(messages: List[Messages]) -> List[ModelMessage]:
    message_history: List[ModelMessage] = []

    for message in messages:
        if message.role == MessageRole.USER:
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=message.content)])
            )
        elif message.role == MessageRole.ASSISTANT:
            message_history.append(
                ModelResponse(
                    parts=[TextPart(content=message.content)]
                    )
                )
    return message_history


class MessageService:
    @staticmethod
    async def generate_response(
        conversation_id: str, data: MessageCreate, db: Session, current_user: TokenData
    ) -> MessageResponse:
        conversation = db.query(Conversations).filter(Conversations.id == conversation_id, current_user.id == Conversations.user_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        db_language_model = (
            db.query(LanguageModels).filter(LanguageModels.id == data.model_id).first()
        )
        if not db_language_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Language model not found"
            )
        message_history = _build_message_history(db.query(Messages).filter(Messages.conversation_id == conversation_id).order_by(Messages.created_at.asc()).limit(20))
        
        new_message = Messages(
            conversation_id=conversation_id,
            role=MessageRole.USER,
            model_id=data.model_id,
            content=data.message,
            message_type=MessageType.TEXT,
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        model = OpenRouterModel(
            model_name=db_language_model.api_identifier,
            provider=OpenRouterProvider(api_key=CONFIG.OPENROUTER_API_KEY),
        )
        agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant.",
        )
        result = await agent.run(data.message, message_history=message_history)
        
        new_agent_message = Messages(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            model_id=data.model_id,
            content=result.output,
            message_type=MessageType.TEXT,
        )
        db.add(new_agent_message)
        db.commit()
        db.refresh(new_agent_message)
        return new_agent_message


    @staticmethod
    def list_messages(db: Session, conversation_id: str, current_user: TokenData) -> list[MessageResponse]:
        conversation = db.query(Conversations).filter(Conversations.id == conversation_id, current_user.id == Conversations.user_id).first()
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )
        messages = db.query(Messages).filter(Messages.conversation_id == conversation_id).order_by(Messages.created_at.asc()).limit(20).all()
        return [message for message in messages]