import json
import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("LLM_API_KEY", "test")
sys.path.append(str(Path(__file__).parents[1] / "src"))

from core.logging import JsonFormatter  # noqa: E402


def test_json_formatter_includes_expected_fields():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )

    payload = json.loads(formatter.format(record))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "hello"
    assert "timestamp" in payload
