from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class TierCreate(BaseModel):
    name: str = Field(
        ..., description="The name of the tier", min_length=1, max_length=100
    )
    price: int = Field(..., description="The price of the tier in naira")
    message_limit: int = Field(..., description="Message limit for the tier", ge=0)
    image_limit: int = Field(..., description="Image limit for the tier", ge=0)
    research_limit: int = Field(..., description="Research limit for the tier", ge=0)
    document_limit: int = Field(..., description="Document limit for the tier", ge=0)
    model_access: list[str] = Field(
        default=[], description="List of model IDs accessible by this tier"
    )
    is_active: bool = Field(default=True, description="Whether the tier is active")


class TierUpdate(BaseModel):
    name: Optional[str] = Field(
        None, description="The name of the tier", min_length=1, max_length=100
    )
    price: Optional[int] = Field(
        None, description="The price of the tier in naira"
    )
    message_limit: Optional[int] = Field(
        None, description="Message limit for the tier", ge=0
    )
    image_limit: Optional[int] = Field(
        None, description="Image limit for the tier", ge=0
    )
    research_limit: Optional[int] = Field(
        None, description="Research limit for the tier", ge=0
    )
    document_limit: Optional[int] = Field(
        None, description="Document limit for the tier", ge=0
    )
    model_access: Optional[list[str]] = Field(
        None, description="List of model IDs accessible by this tier"
    )
    is_active: Optional[bool] = Field(None, description="Whether the tier is active")


class TierResponse(BaseModel):
    id: str = Field(..., description="The unique identifier of the tier")
    name: str = Field(..., description="The name of the tier")
    price: int = Field(..., description="The price of the tier in cents")
    message_limit: int = Field(..., description="Message limit for the tier")
    image_limit: int = Field(..., description="Image limit for the tier")
    research_limit: int = Field(..., description="Research limit for the tier")
    document_limit: int = Field(..., description="Document limit for the tier")
    model_access: list[str] = Field(
        ..., description="List of model IDs accessible by this tier"
    )
    is_active: bool = Field(..., description="Whether the tier is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)
