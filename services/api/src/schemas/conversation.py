from __future__ import annotations

from typing import Any
from uuid import UUID

from core.config import BaseSchema
from pydantic import Field


class ConversationMessageRequest(BaseSchema):
    tenant_id: UUID
    chat_id: UUID
    content: str = Field(min_length=1)
    model: str
    system_prompt: str | None = None
    temperature: float | None = None
    max_tokens: int | None = Field(default=None, ge=1)
    extra: dict[str, Any] | None = None


class ConversationToolCallResult(BaseSchema):
    name: str
    args: dict[str, Any]
    result: list[dict[str, Any]]


class ConversationMessageResponse(BaseSchema):
    content: str
    tool_calls: list[ConversationToolCallResult] = Field(default_factory=list)
