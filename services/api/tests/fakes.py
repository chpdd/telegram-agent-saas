from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from langchain.messages import AIMessage


class FakeStructuredResponder:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[list[Any]] = []

    async def ainvoke(self, messages: Sequence[Any]) -> Any:
        self.calls.append(list(messages))
        return self.response


class FakeChatModel:
    def __init__(self, responses: Sequence[Any]) -> None:
        self.responses = list(responses)
        self.calls: list[list[Any]] = []
        self.bound_tools: list[Any] = []
        self.structured_schema: Any = None
        self.structured_method: str | None = None
        self.structured_responder: FakeStructuredResponder | None = None

    async def ainvoke(self, messages: Sequence[Any]) -> Any:
        self.calls.append(list(messages))
        if not self.responses:
            raise AssertionError("No fake LLM responses left")
        return self.responses.pop(0)

    def bind_tools(self, tools: list[Any]) -> FakeChatModel:
        self.bound_tools = list(tools)
        return self

    def with_structured_output(self, schema: Any, *, method: str) -> FakeStructuredResponder:
        self.structured_schema = schema
        self.structured_method = method
        if not self.responses:
            raise AssertionError("No fake structured response configured")
        responder = FakeStructuredResponder(self.responses.pop(0))
        self.structured_responder = responder
        return responder


def make_ai_message(
    content: str,
    *,
    tool_calls: list[dict[str, Any]] | None = None,
) -> AIMessage:
    kwargs: dict[str, Any] = {}
    if tool_calls is not None:
        kwargs["tool_calls"] = tool_calls
    return AIMessage(content=content, **kwargs)
