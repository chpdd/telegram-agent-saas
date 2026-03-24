import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.example")

sys.path.append(str(Path(__file__).parents[1] / "src"))

from langchain.messages import AIMessage, HumanMessage, SystemMessage  # noqa: E402
from services.ai import (  # noqa: E402
    OpenRouterError,
    chat_completion,
    get_conversation_history,
    reset_conversation_history,
)


@pytest.mark.asyncio
async def test_chat_completion_builds_payload(mocker):
    mock_model = mocker.MagicMock()
    mock_model.ainvoke = mocker.AsyncMock(return_value=AIMessage(content="ok"))
    mocker.patch("services.ai.ChatOpenAI", return_value=mock_model)

    result = await chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        model="gpt-4o",
        temperature=0.2,
        max_tokens=50,
        extra={"top_p": 0.9},
    )

    assert result.content == "ok"
    mock_model.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_chat_completion_rejects_unknown_role(mocker):
    mock_model = mocker.MagicMock()
    mock_model.ainvoke = mocker.AsyncMock()
    mocker.patch("services.ai.ChatOpenAI", return_value=mock_model)

    with pytest.raises(OpenRouterError):
        await chat_completion(messages=[{"role": "tool", "content": "no"}], model="gpt-4o")


@pytest.mark.asyncio
async def test_chat_completion_uses_memory_for_conversation_context(mocker):
    conversation_id = "dialog-1"
    reset_conversation_history(conversation_id)

    mock_model = mocker.MagicMock()
    mock_model.ainvoke = mocker.AsyncMock(
        side_effect=[
            AIMessage(content="first reply"),
            AIMessage(content="second reply"),
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

    first_call_messages = mock_model.ainvoke.await_args_list[0].args[0]
    second_call_messages = mock_model.ainvoke.await_args_list[1].args[0]
    history = get_conversation_history(conversation_id)

    assert isinstance(first_call_messages[0], SystemMessage)
    assert isinstance(first_call_messages[1], HumanMessage)
    assert len(second_call_messages) == 4
    assert isinstance(second_call_messages[2], AIMessage)
    assert isinstance(second_call_messages[3], HumanMessage)
    assert len(history) == 5

    reset_conversation_history(conversation_id)
