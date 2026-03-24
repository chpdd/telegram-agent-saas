import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.example")

API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

from fakes import FakeChatModel, make_ai_message  # noqa: E402
from langchain.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402
from services.ai import (  # noqa: E402
    OpenRouterError,
    build_chat_model,
    chat_completion,
    get_conversation_history,
    reset_conversation_history,
)


@pytest.mark.asyncio
async def test_chat_completion_builds_payload(mocker):
    mock_model = FakeChatModel([make_ai_message("ok")])
    mocker.patch("services.ai.ChatOpenAI", return_value=mock_model)

    result = await chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        model="gpt-4o",
        temperature=0.2,
        max_tokens=50,
        extra={"top_p": 0.9},
    )

    assert result.content == "ok"
    assert len(mock_model.calls) == 1
    assert isinstance(mock_model.calls[0][0], HumanMessage)


@pytest.mark.asyncio
async def test_chat_completion_rejects_unknown_role(mocker):
    mock_model = FakeChatModel([])
    mocker.patch("services.ai.ChatOpenAI", return_value=mock_model)

    with pytest.raises(OpenRouterError):
        await chat_completion(messages=[{"role": "tool", "content": "no"}], model="gpt-4o")


@pytest.mark.asyncio
async def test_chat_completion_uses_memory_for_conversation_context(mocker):
    conversation_id = "dialog-1"
    reset_conversation_history(conversation_id)

    mock_model = FakeChatModel(
        [
            make_ai_message("first reply"),
            make_ai_message("second reply"),
        ]
    )
    mocker.patch("services.ai.ChatOpenAI", return_value=mock_model)

    await chat_completion(
        messages=[
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"},
        ],
        model="gpt-4o",
        conversation_id=conversation_id,
    )
    await chat_completion(
        messages=[{"role": "user", "content": "What is my previous message?"}],
        model="gpt-4o",
        conversation_id=conversation_id,
    )

    first_call_messages = mock_model.calls[0]
    second_call_messages = mock_model.calls[1]
    history = get_conversation_history(conversation_id)

    assert isinstance(first_call_messages[0], SystemMessage)
    assert isinstance(first_call_messages[1], HumanMessage)
    assert len(second_call_messages) == 4
    assert isinstance(second_call_messages[2], AIMessage)
    assert isinstance(second_call_messages[3], HumanMessage)
    assert len(history) == 5

    reset_conversation_history(conversation_id)


def test_build_chat_model_binds_tools(mocker):
    tool = object()
    fake_model = FakeChatModel([AIMessage(content="unused")])
    constructor = mocker.patch("services.ai.ChatOpenAI", return_value=fake_model)

    result = build_chat_model(model="gpt-4o", tools=[tool])

    assert result is fake_model
    constructor.assert_called_once()
    assert fake_model.bound_tools == [tool]
