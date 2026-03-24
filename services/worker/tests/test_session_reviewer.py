import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKER_SRC = str(Path(__file__).parents[1] / "src")
if WORKER_SRC in sys.path:
    sys.path.remove(WORKER_SRC)
sys.path.insert(0, WORKER_SRC)

for module_name in ["session_reviewer"]:
    sys.modules.pop(module_name, None)

from session_reviewer import (  # noqa: E402
    SessionReview,
    build_review_messages,
    review_session,
    serialize_transcript,
)


def test_serialize_transcript_supports_dicts_and_objects():
    transcript = serialize_transcript(
        [
            {"role": "user", "content": "I need a red sofa"},
            SimpleNamespace(role="assistant", content="What size do you need?"),
        ]
    )

    assert transcript == "user: I need a red sofa\nassistant: What size do you need?"


def test_build_review_messages_includes_store_context():
    prompt_messages = build_review_messages(
        [{"role": "user", "content": "Need a desk under 100"}],
        system_prompt="Furniture store assistant",
    )

    assert len(prompt_messages) == 2
    assert "Store context: Furniture store assistant" in prompt_messages[0].content
    assert "user: Need a desk under 100" in prompt_messages[1].content


@pytest.mark.asyncio
async def test_review_session_uses_structured_output(mocker):
    expected = SessionReview(
        summary="Customer asked for a sofa and price range.",
        sentiment="neutral",
        customer_intent="Find a sofa within budget.",
        missed_opportunities=["No upsell on delivery service."],
        recommendations=["Offer delivery earlier in the dialog."],
    )
    reviewer = mocker.MagicMock()
    reviewer.ainvoke = mocker.AsyncMock(return_value=expected)
    model = mocker.MagicMock()
    model.with_structured_output.return_value = reviewer

    result = await review_session(
        [{"role": "user", "content": "Need a sofa"}],
        model=model,
        system_prompt="Furniture store assistant",
    )

    assert result == expected
    model.with_structured_output.assert_called_once_with(SessionReview, method="json_schema")
    reviewer.ainvoke.assert_awaited_once()
