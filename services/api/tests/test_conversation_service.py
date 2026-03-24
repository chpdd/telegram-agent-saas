import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from langchain.messages import AIMessage, ToolMessage  # noqa: E402
from services.ai import get_conversation_history, reset_conversation_history  # noqa: E402
from services.conversation import run_conversation_turn  # noqa: E402


class FakeSession:
    def __init__(self, mocker):
        self.items = []
        self.add = mocker.MagicMock(side_effect=self.items.append)
        self.commit = mocker.AsyncMock()
        self.refresh = mocker.AsyncMock()


@pytest.mark.asyncio
async def test_run_conversation_turn_without_tool_calls(mocker):
    session = FakeSession(mocker)
    tenant_id = uuid4()
    chat_id = uuid4()
    conversation_id = "chat-no-tool"
    reset_conversation_history(conversation_id)

    model = mocker.MagicMock()
    model.ainvoke = mocker.AsyncMock(return_value=AIMessage(content="assistant reply"))
    mocker.patch("services.conversation.build_chat_model", return_value=model)
    mocker.patch("services.conversation.build_catalog_tool", return_value=mocker.MagicMock())

    result = await run_conversation_turn(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id=conversation_id,
        user_content="hello",
        model="gpt-4o",
        system_prompt="be helpful",
    )

    assert result["content"] == "assistant reply"
    assert result["tool_calls"] == []
    assert len(session.items) == 2
    assert len(get_conversation_history(conversation_id)) == 3
    reset_conversation_history(conversation_id)


@pytest.mark.asyncio
async def test_run_conversation_turn_with_catalog_tool(mocker):
    session = FakeSession(mocker)
    tenant_id = uuid4()
    chat_id = uuid4()
    conversation_id = "chat-tool"
    reset_conversation_history(conversation_id)

    model = mocker.MagicMock()
    model.ainvoke = mocker.AsyncMock(
        side_effect=[
            AIMessage(
                content="",
                tool_calls=[{"name": "catalog_tool", "args": {"filters": []}, "id": "call-1"}],
            ),
            AIMessage(content="found products"),
        ]
    )
    catalog_tool = mocker.MagicMock()
    catalog_tool.ainvoke = mocker.AsyncMock(return_value=[{"name": "Sneakers"}])

    mocker.patch("services.conversation.build_chat_model", return_value=model)
    mocker.patch("services.conversation.build_catalog_tool", return_value=catalog_tool)

    result = await run_conversation_turn(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id=conversation_id,
        user_content="find red shoes",
        model="gpt-4o",
    )

    second_call_messages = model.ainvoke.await_args_list[1].args[0]

    assert result["content"] == "found products"
    assert result["tool_calls"] == [
        {"name": "catalog_tool", "args": {"filters": []}, "result": [{"name": "Sneakers"}]}
    ]
    assert any(isinstance(message, ToolMessage) for message in second_call_messages)
    assert len(session.items) == 2
    assert len(get_conversation_history(conversation_id)) == 4
    reset_conversation_history(conversation_id)
