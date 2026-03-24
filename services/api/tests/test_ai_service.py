import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("OPENROUTER_BASE_URL", "https://openrouter.example")

sys.path.append(str(Path(__file__).parents[1] / "src"))

from langchain_core.messages import AIMessage  # noqa: E402
from services.ai import OpenRouterError, chat_completion  # noqa: E402


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
