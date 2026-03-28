from pydantic_ai import Agent
from pydantic_ai.models.openrouter import OpenRouterModel
from app.core.config import CONFIG
from pydantic_ai.providers.openrouter import OpenRouterProvider
from app.domains.messages.schemas import MessageCreate, MessageResponse
from uuid import uuid7
from datetime import datetime, timezone


class MessageService:
    @staticmethod
    async def generate_response(user_id: str, model_name: str, conversation_id: str, message: str) -> str:
        model = OpenRouterModel(
            model_name=model_name,
            provider=OpenRouterProvider(
                api_key=CONFIG.OPENROUTER_API_KEY
            )
        )
        agent = Agent(
            model=model,
            system_prompt="You are a helpful assistant.",
        )
        result = await agent.run(message)
        return MessageResponse(
            id=str(uuid7()),
            conversation_id=conversation_id,
            role="assistant",
            content=result.output,
            message_type="text",
            message_metadata=None,
            file_url=None,
            file_name=None,
            file_size_bytes=None,
            tools=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    