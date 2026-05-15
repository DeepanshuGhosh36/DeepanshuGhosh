from __future__ import annotations

from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


class Message(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(min_length=1, max_length=4000)


class Recommendation(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    test_type: str = Field(min_length=1, max_length=120)


class ChatRequest(BaseModel):
    messages: List[Message] = Field(min_length=1, max_length=100)


class ChatResponse(BaseModel):
    reply: str = Field(min_length=1, max_length=4000)
    recommendations: List[Recommendation] = Field(default_factory=list)
    end_of_conversation: bool = False

    @field_validator("recommendations")
    @classmethod
    def validate_recommendation_count(cls, value: List[Recommendation]) -> List[Recommendation]:
        if len(value) > 10:
            raise ValueError("recommendations must contain at most 10 items")
        return value
