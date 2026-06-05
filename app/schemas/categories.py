from pydantic import BaseModel, ConfigDict, field_validator
from typing import List
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be blank")
        if len(v) > 255:
            raise ValueError("name must not exceed 255 characters")
        return v


class CategoryOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryList(BaseModel):
    categories: List[CategoryOut]

    model_config = ConfigDict(from_attributes=True)
