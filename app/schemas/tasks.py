from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_completed: Optional[bool] = False
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title must not be blank")
        if len(v) > 255:
            raise ValueError("title must not exceed 255 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 5000:
            raise ValueError("description must not exceed 5000 characters")
        return v

    @field_validator("category_id")
    @classmethod
    def category_id_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("category_id must be a positive integer")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    category_id: Optional[int] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("title must not be blank")
            if len(v) > 255:
                raise ValueError("title must not exceed 255 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_max_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 5000:
            raise ValueError("description must not exceed 5000 characters")
        return v

    @field_validator("category_id")
    @classmethod
    def category_id_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v <= 0:
            raise ValueError("category_id must be a positive integer")
        return v


class TaskResponse(BaseModel):
    id: str
    category_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
