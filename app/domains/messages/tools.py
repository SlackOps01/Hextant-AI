import httpx
import base64
from dataclasses import dataclass
from sqlalchemy.orm import Session
from fastapi.concurrency import run_in_threadpool

from pydantic_ai import RunContext
from app.core.logging import logger
from app.core.config import CONFIG
from app.domains.artifacts.service import ArtifactService
from app.domains.artifacts.models import ArtifactType

@dataclass
class AgentDeps:
    db: Session
    user_id: str
    message_id: str
    image_model_id: str

async def generate_image_tool(ctx: RunContext[AgentDeps], image_prompt: str) -> str:
    """
    Use this tool WHENEVER the user asks to generate, create, or draw an image.
    Args:
        image_prompt: A highly detailed, descriptive prompt for the image.
    """
    artifact_service = ArtifactService()
    image_model_id = ctx.deps.image_model_id or "sourceful/riverflow-v2-fast"

    async with httpx.AsyncClient() as client:
        try:
            # 1. Ask OpenRouter to generate the image using the specific image modalities format
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {CONFIG.OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": image_model_id,
                    "messages": [{"role": "user", "content": image_prompt}],
                    "modalities": ["image"]  # CRITICAL: Tells OpenRouter to return an image object
                },
                timeout=45.0
            )
            response.raise_for_status()
            
            # 2. Parse the OpenRouter specific image response
            response_data = response.json()
            choices = response_data.get("choices", [])
            
            if not choices:
                logger.error(f"No choices returned from OpenRouter. Raw response: {response_data}")
                return "Error: The image provider returned an invalid response format."
                
            message = choices[0].get("message", {})
            images = message.get("images", [])
            
            if not images:
                logger.error(f"No images found in the message object. Raw response: {response_data}")
                return "Error: The model failed to generate an image."

            # 3. Extract the image URL (which is a Base64 data URL according to the docs)
            image_data_url = images[0].get("image_url", {}).get("url")
            
            if not image_data_url:
                logger.error(f"Missing 'url' field in image object. Raw images data: {images}")
                return "Error: The image provider returned an empty image payload."

            # 4. Extract bytes from the Base64 Data URL or download if it's a standard URL
            if image_data_url.startswith("data:image"):
                # Split 'data:image/png;base64,iVBORw0K...' into header and base64 payload
                _, encoded_data = image_data_url.split(",", 1)
                image_bytes = base64.b64decode(encoded_data)
            elif image_data_url.startswith("http"):
                # Fallback just in case OpenRouter returns a standard URL for a different model
                img_response = await client.get(image_data_url, timeout=20.0)
                img_response.raise_for_status()
                image_bytes = img_response.content
            else:
                return "Error: Unrecognized image URL format returned by the provider."

            # 5. Save using your ArtifactService on a separate thread to avoid blocking
            def save_artifact():
                artifact = artifact_service.upload_artifact(
                    ctx.deps.db, 
                    ArtifactType.IMAGE, 
                    image_bytes, 
                    ctx.deps.user_id,
                    ctx.deps.message_id
                )
                return artifact_service.generate_artifact_url(ctx.deps.db, artifact.id, ctx.deps.user_id)
            
            attachment_url = await run_in_threadpool(save_artifact)

            # 6. Return your internal URL to the main agent
            return f"Image generated successfully. Show this exactly to the user: ![Generated Image]({attachment_url})"

        except httpx.HTTPError as e:
            error_msg = f"API Error generating image with {image_model_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error generating image with {image_model_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg