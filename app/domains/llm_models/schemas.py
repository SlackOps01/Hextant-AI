from pydantic import ConfigDict
from typing import Optional
from pydantic import BaseModel, Field
from app.domains.llm_models.models import ModelType, ModelModality
from datetime import datetime, timezone

class LanguageModelCreate(BaseModel):
    display_name: str = Field(..., description="The display name of the model", examples=["GPT-4"])
    model_type: ModelType = Field(..., description="The type of the model", examples=[ModelType.TEXT])
    modality: ModelModality = Field(..., description="The modality of the model", examples=[ModelModality.TEXT])
    context_length: int = Field(..., description="The context length of the model", examples=[4096])
    provider: str = Field(..., description="The provider of the model", examples=["OpenAI"])
    input_token_price: float = Field(..., description="The input token price of the model", examples=[1])
    output_token_price: float = Field(..., description="The output token price of the model", examples=[1])
    api_identifier: str = Field(..., description="The api identifier for the model", examples=["xiaomi/mimo-v2-pro"])
    adapter: Optional[str] =  Field(None, description="The adapter for the model", examples=["generic"])


class LanguageModelResponse(BaseModel):
    id: str = Field(..., description="The id of the model", examples=["123e4567-e89b-12d3-a456-426614174000"])
    display_name: str = Field(..., description="The display name of the model", examples=["GPT-4"])
    model_type: ModelType = Field(..., description="The type of the model", examples=[ModelType.TEXT])
    modality: ModelModality = Field(..., description="The modality of the model", examples=[ModelModality.TEXT])
    context_length: int = Field(..., description="The context length of the model", examples=[4096])
    provider: str = Field(..., description="The provider of the model", examples=["OpenAI"])
    input_token_price: float = Field(..., description="The input token price of the model", examples=[1])
    output_token_price: float = Field(..., description="The output token price of the model", examples=[1])
    api_identifier: str = Field(..., description="The api identifier for the model", examples=["xiaomi/mimo-v2-pro"])
    adapter: Optional[str] =  Field(None, description="The adapter for the model", examples=["generic"])
    created_at: datetime = Field(..., description="The creation timestamp of the model", examples=[datetime.now(timezone.utc)])
    updated_at: datetime = Field(..., description="The update timestamp of the model", examples=[datetime.now(timezone.utc)])


    model_config = ConfigDict(from_attributes=True)