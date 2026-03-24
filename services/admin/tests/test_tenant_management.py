import sys
from pathlib import Path
from uuid import UUID

import pytest

sys.path.append(str(Path(__file__).parents[1] / "src"))

from tenant_management import create_tenant, list_tenants, mask_bot_token, prepare_tenant_payload  # noqa: E402


def test_prepare_tenant_payload_generates_uuid_and_normalizes_fields():
    payload = prepare_tenant_payload(None, "  token-123  ", "  assistant  ")

    assert isinstance(payload["tenant_id"], UUID)
    assert payload["bot_token"] == "token-123"
    assert payload["system_prompt"] == "assistant"


def test_prepare_tenant_payload_validates_uuid():
    with pytest.raises(ValueError, match="UUID"):
        prepare_tenant_payload("not-a-uuid", "token-123", None)


def test_mask_bot_token_hides_middle_part():
    assert mask_bot_token("1234567890abcdef") == "1234...cdef"
    assert mask_bot_token("12345678") == "********"


def test_create_tenant_executes_insert_and_commit(mocker):
    session = mocker.Mock()

    created = create_tenant(
        session,
        tenant_id="11111111-1111-1111-1111-111111111111",
        bot_token="bot-token",
        system_prompt="assistant",
    )

    assert created == {
        "tenant_id": "11111111-1111-1111-1111-111111111111",
        "bot_token": "bot-token",
        "system_prompt": "assistant",
    }
    session.execute.assert_called_once()
    session.commit.assert_called_once()


def test_list_tenants_masks_tokens(mocker):
    rows = [
        {
            "id": UUID("11111111-1111-1111-1111-111111111111"),
            "bot_token": "1234567890abcdef",
            "system_prompt": "assistant",
        }
    ]
    result = mocker.Mock()
    result.mappings.return_value.all.return_value = rows
    session = mocker.Mock()
    session.execute.return_value = result

    tenants = list_tenants(session)

    assert tenants == [
        {
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "bot_token": "1234...cdef",
            "system_prompt": "assistant",
        }
    ]
