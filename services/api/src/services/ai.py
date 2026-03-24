from __future__ import annotations

from typing import Any

from core.config import settings
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class OpenRouterError(ValueError):
    pass


def _to_message(item: dict[str, Any]):
    role = item.get("role")
    content = item.get("content", "")
    if role == "system":
        return SystemMessage(content=content)
    if role == "user":
        return HumanMessage(content=content)
    if role == "assistant":
        return AIMessage(content=content)
    raise OpenRouterError(f"Unsupported role: {role}")


def _build_model(
    model: str,
    *,
    temperature: float | None,
    max_tokens: int | None,
    extra: dict[str, Any] | None,
) -> ChatOpenAI:
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL,
        model_kwargs=extra or {},
    )


async def chat_completion(
    *,
    messages: list[dict[str, Any]],
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra: dict[str, Any] | None = None,
) -> AIMessage:
    model_client = _build_model(
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        extra=extra,
    )
    formatted = [_to_message(item) for item in messages]
    return await model_client.ainvoke(formatted)
