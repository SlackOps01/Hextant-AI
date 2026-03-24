from typing import Optional
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.networks import AnyUrl
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(..., description="User's username", min_length=3, max_length=50)
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password", min_length=8, max_length=64)
    profile_picture_url: AnyUrl | None = Field(None, description="User's profile picture URL")


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="User's username", min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, description="User's email address")
    password: Optional[str] = Field(None, description="User's password", min_length=8, max_length=64)
    profile_picture_url: Optional[AnyUrl] =  Field(None, description="User's profile picture URL")



class UserResponse(BaseModel):
    id: str 
    username: str
    email: EmailStr
    role: str
    profile_picture_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # The modern Pydantic V2 way to allow ORM models
    model_config = ConfigDict(from_attributes=True)