from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from langchain.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field


class SessionReview(BaseModel):
    summary: str
    sentiment: Literal["positive", "neutral", "negative"]
    customer_intent: str
    missed_opportunities: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


def _message_role(item: Any) -> str:
    if isinstance(item, dict):
        return str(item["role"])
    return str(item.role)


def _message_content(item: Any) -> str:
    if isinstance(item, dict):
        return str(item["content"])
    return str(item.content)


def serialize_transcript(messages: Sequence[Any]) -> str:
    lines = [f"{_message_role(item)}: {_message_content(item)}" for item in messages]
    return "\n".join(lines)


def build_review_messages(
    messages: Sequence[Any],
    *,
    system_prompt: str | None = None,
) -> list[Any]:
    system_content = (
        "You are an analyst for a multi-tenant Telegram sales assistant. "
        "Review the completed conversation and extract structured business insights. "
        "Use only facts from the transcript."
    )
    if system_prompt:
        system_content = f"{system_content}\nStore context: {system_prompt}"

    transcript = serialize_transcript(messages)
    prompt = (
        "Review this conversation transcript.\n"
        "Return a concise summary, overall sentiment, main customer intent, "
        "missed sales opportunities, and actionable recommendations.\n\n"
        f"{transcript}"
    )
    return [
        SystemMessage(content=system_content),
        HumanMessage(content=prompt),
    ]


async def review_session(
    messages: Sequence[Any],
    *,
    model: Any,
    system_prompt: str | None = None,
) -> SessionReview:
    reviewer = model.with_structured_output(SessionReview, method="json_schema")
    return await reviewer.ainvoke(build_review_messages(messages, system_prompt=system_prompt))
