from __future__ import annotations

import json
from time import perf_counter
from typing import Any
from uuid import UUID

from langchain.messages import AIMessage, ToolMessage
from models.message import Message, MessageRole
from services.ai import (
    append_conversation_history,
    build_chat_model,
    get_conversation_history,
    to_langchain_message,
)
from services.catalog_tool import build_catalog_tool
from sqlalchemy.ext.asyncio import AsyncSession


async def _persist_message(
    session: AsyncSession,
    *,
    tenant_id: UUID | str,
    chat_id: UUID | str,
    role: MessageRole,
    content: str,
    latency_ms: int | None = None,
) -> Message:
    message = Message(
        tenant_id=tenant_id,
        chat_id=chat_id,
        role=role,
        content=content,
        latency_ms=latency_ms,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return message


def _serialize_tool_result(result: Any) -> str:
    return json.dumps(result, ensure_ascii=False, default=str)


def _message_content(message: AIMessage) -> str:
    if isinstance(message.content, str):
        return message.content
    return json.dumps(message.content, ensure_ascii=False, default=str)


async def run_conversation_turn(
    session: AsyncSession,
    *,
    tenant_id: UUID | str,
    chat_id: UUID | str,
    conversation_id: str,
    user_content: str,
    model: str,
    system_prompt: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    await _persist_message(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        role=MessageRole.USER,
        content=user_content,
    )

    catalog_tool = build_catalog_tool(session, tenant_id)
    model_with_tools = build_chat_model(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        extra=extra,
        tools=[catalog_tool],
    )

    incoming_messages: list[dict[str, str]] = []
    if system_prompt and not get_conversation_history(conversation_id):
        incoming_messages.append({"role": "system", "content": system_prompt})
    incoming_messages.append({"role": "user", "content": user_content})

    history = [*get_conversation_history(conversation_id)]
    new_messages: list[Any] = []
    for item in incoming_messages:
        message = to_langchain_message(item)
        history.append(message)
        new_messages.append(message)

    started_at = perf_counter()
    ai_message = await model_with_tools.ainvoke(history)

    if not ai_message.tool_calls:
        latency_ms = int((perf_counter() - started_at) * 1000)
        content = _message_content(ai_message)
        append_conversation_history(conversation_id, [*new_messages, ai_message])
        await _persist_message(
            session,
            tenant_id=tenant_id,
            chat_id=chat_id,
            role=MessageRole.ASSISTANT,
            content=content,
            latency_ms=latency_ms,
        )
        return {"content": content, "tool_calls": []}

    history.append(ai_message)
    new_messages.append(ai_message)
    tool_results: list[dict[str, Any]] = []
    for tool_call in ai_message.tool_calls:
        if tool_call["name"] != "catalog_tool":
            continue

        result = await catalog_tool.ainvoke(tool_call["args"])
        tool_results.append({"name": tool_call["name"], "args": tool_call["args"], "result": result})
        tool_message = ToolMessage(
            content=_serialize_tool_result(result),
            tool_call_id=tool_call["id"],
        )
        history.append(tool_message)
        new_messages.append(tool_message)

    final_message = await model_with_tools.ainvoke(history)
    latency_ms = int((perf_counter() - started_at) * 1000)
    content = _message_content(final_message)
    append_conversation_history(conversation_id, [*new_messages, final_message])
    await _persist_message(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        role=MessageRole.ASSISTANT,
        content=content,
        latency_ms=latency_ms,
    )
    return {
        "content": content,
        "tool_calls": tool_results,
    }
