from __future__ import annotations

from typing import Any

from core.config import settings
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


class OpenRouterError(ValueError):
    pass


_MEMORY: dict[str, list[Any]] = {}


def to_langchain_message(item: dict[str, Any]) -> Any:
    role = item.get("role")
    content = item.get("content", "")
    if role == "system":
        return SystemMessage(content=content)
    if role == "user":
        return HumanMessage(content=content)
    if role == "assistant":
        return AIMessage(content=content)
    raise OpenRouterError(f"Unsupported role: {role}")


def get_conversation_history(conversation_id: str) -> list[Any]:
    return list(_MEMORY.get(conversation_id, []))


def append_conversation_history(conversation_id: str, messages: list[Any]) -> None:
    history = _MEMORY.setdefault(conversation_id, [])
    history.extend(messages)


def reset_conversation_history(conversation_id: str) -> None:
    _MEMORY.pop(conversation_id, None)


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


def build_chat_model(
    *,
    model: str,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra: dict[str, Any] | None = None,
    tools: list[Any] | None = None,
) -> ChatOpenAI:
    chat_model = _build_model(
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        extra=extra,
    )
    if tools:
        return chat_model.bind_tools(tools)
    return chat_model


async def chat_completion(
    *,
    messages: list[dict[str, Any]],
    model: str,
    conversation_id: str | None = None,
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
    formatted = [to_langchain_message(item) for item in messages]
    if conversation_id:
        history = _MEMORY.setdefault(conversation_id, [])
        request_messages = [*history, *formatted]
    else:
        history = None
        request_messages = formatted

    response = await model_client.ainvoke(request_messages)

    if history is not None:
        history.extend(formatted)
        history.append(response)

    return response
