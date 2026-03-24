import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest

os.environ.setdefault("LLM_API_KEY", "test")
API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

from fakes import FakeChatModel, make_ai_message  # noqa: E402
from langchain.messages import AIMessage, ToolMessage  # noqa: E402
from models.message import MessageRole  # noqa: E402
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


@pytest.mark.asyncio
async def test_e2e_bot_conversation_persists_messages_and_reuses_history(mocker):
    session = FakeSession(mocker)
    tenant_id = uuid4()
    chat_id = uuid4()
    conversation_id = "chat-e2e"
    reset_conversation_history(conversation_id)

    model = FakeChatModel(
        [
            make_ai_message(
                "",
                tool_calls=[
                    {
                        "name": "catalog_tool",
                        "args": {"filters": [{"field": "color", "op": "eq", "value": "red"}]},
                        "id": "call-1",
                    }
                ],
            ),
            make_ai_message("I found a red chair for you."),
            make_ai_message("It is still available and costs 50."),
        ]
    )
    catalog_tool = mocker.MagicMock()
    catalog_tool.ainvoke = mocker.AsyncMock(
        return_value=[
            {
                "id": str(uuid4()),
                "tenant_id": str(tenant_id),
                "name": "Red Chair",
                "description": "Compact chair",
                "attributes": {"color": "red", "price": 50},
            }
        ]
    )

    mocker.patch("services.conversation.build_chat_model", return_value=model)
    mocker.patch("services.conversation.build_catalog_tool", return_value=catalog_tool)

    first_result = await run_conversation_turn(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id=conversation_id,
        user_content="Find a red chair",
        model="gpt-4o",
        system_prompt="You are a furniture store assistant",
    )
    second_result = await run_conversation_turn(
        session,
        tenant_id=tenant_id,
        chat_id=chat_id,
        conversation_id=conversation_id,
        user_content="Is it still available?",
        model="gpt-4o",
    )

    history = get_conversation_history(conversation_id)
    first_model_call = model.calls[0]
    second_model_call = model.calls[2]
    persisted_roles = [item.role for item in session.items]
    persisted_contents = [item.content for item in session.items]

    assert first_result["content"] == "I found a red chair for you."
    assert first_result["tool_calls"][0]["result"][0]["name"] == "Red Chair"
    assert second_result["content"] == "It is still available and costs 50."
    assert first_model_call[0].content == "You are a furniture store assistant"
    assert any(isinstance(message, ToolMessage) for message in model.calls[1])
    assert any(
        isinstance(message, AIMessage) and message.content == "I found a red chair for you."
        for message in second_model_call
    )
    assert len(history) == 7
    assert persisted_roles == [
        MessageRole.USER,
        MessageRole.ASSISTANT,
        MessageRole.USER,
        MessageRole.ASSISTANT,
    ]
    assert persisted_contents == [
        "Find a red chair",
        "I found a red chair for you.",
        "Is it still available?",
        "It is still available and costs 50.",
    ]

    reset_conversation_history(conversation_id)
