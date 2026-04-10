from app.core.logging import logger
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai import TextPart, ImageUrl, VideoUrl, AudioUrl, DocumentUrl, Tool
from pydantic_ai import ModelRequest, ModelResponse
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
from app.domains.attachments.service import AttachmentService, AttachmentNotFoundException
from app.domains.attachments.models import Attachments
from fastapi.concurrency import run_in_threadpool
from pydantic_ai.common_tools.tavily import tavily_search_tool
from app.core.prompts import system_prompt
from app.domains.messages.tools import AgentDeps, generate_image_tool


class LanguageModelNotFound(HTTPException):
    def __init__(self, model_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Language model with id {model_id} not found")

class ConversationNotFound(HTTPException):
    def __init__(self, conversation_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conversation with id {conversation_id} not found")

class ModelFeatureNotSupportedError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

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
        
        def fetch_initial_data():
            conversation = db.query(Conversations).filter(
                Conversations.id == conversation_id, 
                current_user.id == Conversations.user_id
            ).first()
            if not conversation:
                raise ConversationNotFound(conversation_id)
            
            db_language_model = db.query(LanguageModels).filter(LanguageModels.id == data.model_id).first()
            if not db_language_model:
                raise LanguageModelNotFound(data.model_id)
                
            messages = db.query(Messages).filter(
                Messages.conversation_id == conversation_id
            ).order_by(Messages.created_at.desc()).limit(30).all()
            messages.reverse()
            
            return db_language_model, messages

        db_language_model, db_messages = await run_in_threadpool(fetch_initial_data)
        message_history = _build_message_history(db_messages)
        message = [data.message]
        
        if data.attachments:
            def process_attachments():
                urls = []
                for attachment_id in data.attachments:
                    attachment = db.query(Attachments).filter(Attachments.id == attachment_id).first()
                    if not attachment:
                        raise AttachmentNotFoundException(attachment_id)
                    url = AttachmentService.generate_download_url(db, attachment.id, current_user.id)
                    urls.append((attachment.mime_type, url))
                return urls
                
            attachment_data = await run_in_threadpool(process_attachments)
            for mime_type, url in attachment_data:
                if mime_type.startswith("image/"):
                    message.append(ImageUrl(url=url))
                elif mime_type.startswith("audio/"):
                    message.append(AudioUrl(url=url))
                elif mime_type.startswith("video/"):
                    message.append(VideoUrl(url=url))
                else:
                    message.append(DocumentUrl(url=url))

        def save_user_message():
            new_msg = Messages(
                conversation_id=conversation_id,
                role=MessageRole.USER,
                model_id=data.model_id,
                content=data.message,
                message_type=MessageType.TEXT,
            )
            db.add(new_msg)
            db.commit()
            db.refresh(new_msg)
            return new_msg
            
        new_message = await run_in_threadpool(save_user_message)
        deps = AgentDeps(
            db=db,
            user_id=current_user.id,
            message_id=new_message.id,
            image_model_id=data.image_model_id 
        )
        model = OpenRouterModel(
            model_name=db_language_model.api_identifier,
            provider=OpenRouterProvider(api_key=CONFIG.OPENROUTER_API_KEY),
        )
        try:
            agent = Agent(
                model=model,
                system_prompt=system_prompt,
                instructions=system_prompt,
                tools=[
                    tavily_search_tool(api_key=CONFIG.TAVILY_API_KEY),
                    Tool(generate_image_tool)
                ]
            )
            
            result = await agent.run(message, message_history=message_history, deps=deps)
            
            def save_agent_message(output):
                new_agent_msg = Messages(
                    conversation_id=conversation_id,
                    role=MessageRole.ASSISTANT,
                    model_id=data.model_id,
                    content=output,
                    message_type=MessageType.TEXT,
                )
                db.add(new_agent_msg)
                db.commit()
                db.refresh(new_agent_msg)
                return new_agent_msg
                
            new_agent_message = await run_in_threadpool(lambda: save_agent_message(result.output))
            return new_agent_message

        except ModelHTTPError as e:
            logger.error(f"Model HTTP Error: {str(e)}")
            raise ModelFeatureNotSupportedError(str(e))



    @staticmethod
    def list_messages(db: Session, conversation_id: str, current_user: TokenData) -> list[MessageResponse]:
        conversation = db.query(Conversations).filter(Conversations.id == conversation_id, current_user.id == Conversations.user_id).first()
        if not conversation:
            raise ConversationNotFound(conversation_id)
        messages = db.query(Messages).filter(Messages.conversation_id == conversation_id).order_by(Messages.created_at.desc()).limit(30).all()
        messages.reverse()
        return [message for message in messages]