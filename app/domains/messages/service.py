import json
import asyncio
from typing import AsyncGenerator, List

from app.core.logging import logger
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai import TextPart, ImageUrl, VideoUrl, AudioUrl, DocumentUrl, Tool
from pydantic_ai import ModelRequest, ModelResponse
from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider
from pydantic_ai.messages import (
    ModelMessage,
    UserPromptPart,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
)
from app.core.config import CONFIG
from app.core.oauth2 import TokenData
from app.core.prompts import system_prompt
from app.domains.messages.schemas import MessageCreate, MessageResponse, StreamDoneEvent
from app.domains.messages.models import Messages, MessageRole, MessageType
from app.domains.llm_models.models import LanguageModels
from app.domains.conversations.models import Conversations
from app.domains.attachments.service import AttachmentService, AttachmentNotFoundException
from app.domains.attachments.models import Attachments
from app.domains.messages.tools import AgentDeps, generate_image_tool
from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from pydantic_ai.common_tools.tavily import tavily_search_tool


class LanguageModelNotFound(HTTPException):
    def __init__(self, model_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Language model with id {model_id} not found")

class ConversationNotFound(HTTPException):
    def __init__(self, conversation_id: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conversation with id {conversation_id} not found")

class ModelFeatureNotSupportedError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


def _format_sse(event: str, data: dict | str) -> str:
    """Format a single SSE event string."""
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n"


def _build_message_history(messages: List[Messages]) -> List[ModelMessage]:
    message_history: List[ModelMessage] = []
    for message in messages:
        if message.role == MessageRole.USER:
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=message.content)])
            )
        elif message.role == MessageRole.ASSISTANT:
            message_history.append(
                ModelResponse(parts=[TextPart(content=message.content)])
            )
    return message_history


class MessageService:
    @staticmethod
    async def validate_and_prepare(
        conversation_id: str, data: MessageCreate, db: Session, current_user: TokenData
    ) -> tuple:
        """Pre-flight validation and setup. Runs BEFORE the stream starts so that
        HTTP errors (404, 400) are returned as normal JSON responses, not swallowed
        into the SSE stream.

        Returns: (agent, message_parts, message_history, user_message, deps, conversation_id)
        """

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
        message_parts = [data.message]

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
                    message_parts.append(ImageUrl(url=url))
                elif mime_type.startswith("audio/"):
                    message_parts.append(AudioUrl(url=url))
                elif mime_type.startswith("video/"):
                    message_parts.append(VideoUrl(url=url))
                else:
                    message_parts.append(DocumentUrl(url=url))

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

        user_message = await run_in_threadpool(save_user_message)

        deps = AgentDeps(
            db=db,
            user_id=current_user.id,
            message_id=user_message.id,
            image_model_id=data.image_model_id
        )

        model = OpenRouterModel(
            model_name=db_language_model.api_identifier,
            provider=OpenRouterProvider(api_key=CONFIG.OPENROUTER_API_KEY),
        )

        agent = Agent(
            model=model,
            system_prompt=system_prompt,
            instructions=system_prompt,
            tools=[
                tavily_search_tool(api_key=CONFIG.TAVILY_API_KEY),
                Tool(generate_image_tool)
            ]
        )

        return agent, message_parts, message_history, user_message, deps, conversation_id, data.model_id

    @staticmethod
    async def stream_response(
        agent: Agent,
        message_parts: list,
        message_history: list,
        user_message: Messages,
        deps: AgentDeps,
        conversation_id: str,
        model_id: str,
        db: Session,
    ) -> AsyncGenerator[str, None]:
        """Async generator that yields SSE events:
        - event: tool_start  — when a tool call begins (tool name)
        - event: tool_end    — when a tool call completes
        - event: token       — each text chunk from the LLM
        - event: done        — final message metadata after DB save
        - event: error       — if something breaks mid-stream
        """
        events_queue: asyncio.Queue[dict] = asyncio.Queue()

        async def run_agent():
            try:
                async def event_stream_handler(ctx, events):
                    """Captures tool call and result events from pydantic-ai."""
                    async for event in events:
                        if isinstance(event, FunctionToolCallEvent):
                            tool_name = event.part.tool_name
                            await events_queue.put({"type": "tool_start", "tool": tool_name})
                        elif isinstance(event, FunctionToolResultEvent):
                            tool_name = getattr(event.result, "tool_name", "unknown")
                            await events_queue.put({"type": "tool_end", "tool": tool_name})

                # run_stream handles the tool calls before yielding text
                async with agent.run_stream(
                    message_parts,
                    message_history=message_history,
                    deps=deps,
                    event_stream_handler=event_stream_handler,
                ) as result:
                    async for chunk in result.stream_text(delta=True):
                        await events_queue.put({"type": "token", "text": chunk})

                await events_queue.put({"type": "internal_done"})

            except ModelHTTPError as e:
                logger.error(f"Model HTTP Error during stream: {str(e)}")
                await events_queue.put({"type": "error", "error": str(e)})
            except Exception as e:
                logger.error(f"Unexpected error during stream: {str(e)}")
                await events_queue.put({"type": "error", "error": "An internal error occurred during generation."})

        # Run the agent in the background so we can stream tool events instantly
        # while run_stream is blocking on tool execution
        task = asyncio.create_task(run_agent())

        tools_used: list[str] = []
        full_text = ""

        try:
            while True:
                event = await events_queue.get()
                
                if event["type"] == "tool_start":
                    tools_used.append(event["tool"])
                    yield _format_sse("tool_start", {"tool": event["tool"]})
                
                elif event["type"] == "tool_end":
                    yield _format_sse("tool_end", {"tool": event["tool"]})
                    
                elif event["type"] == "token":
                    full_text += event["text"]
                    yield _format_sse("token", {"text": event["text"]})
                    
                elif event["type"] == "error":
                    yield _format_sse("error", {"error": event.get("error")})
                    break
                    
                elif event["type"] == "internal_done":
                    # Stream is complete — save the assistant message to DB
                    def save_agent_message():
                        new_agent_msg = Messages(
                            conversation_id=conversation_id,
                            role=MessageRole.ASSISTANT,
                            model_id=model_id,
                            content=full_text,
                            message_type=MessageType.TEXT,
                            tools=tools_used if tools_used else None,
                        )
                        db.add(new_agent_msg)
                        db.commit()
                        db.refresh(new_agent_msg)
                        return new_agent_msg

                    saved_message = await run_in_threadpool(save_agent_message)

                    done_event = StreamDoneEvent(
                        message_id=saved_message.id,
                        conversation_id=conversation_id,
                        content=full_text,
                        tools_used=tools_used,
                    )
                    yield _format_sse("done", done_event.model_dump())
                    break
        finally:
            task.cancel()  # Ensure background task stops if client disconnects

    @staticmethod
    def list_messages(db: Session, conversation_id: str, current_user: TokenData) -> list[MessageResponse]:
        conversation = db.query(Conversations).filter(
            Conversations.id == conversation_id,
            current_user.id == Conversations.user_id
        ).first()
        if not conversation:
            raise ConversationNotFound(conversation_id)
        messages = db.query(Messages).filter(
            Messages.conversation_id == conversation_id
        ).order_by(Messages.created_at.desc()).limit(30).all()
        messages.reverse()
        return [message for message in messages]