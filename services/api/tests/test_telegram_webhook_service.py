from services.telegram_webhook import build_chat_session_id, extract_message_context


def test_extract_message_context_returns_text_payload():
    context = extract_message_context(
        {
            "message": {
                "text": "hello",
                "chat": {"id": 12345},
                "from": {"id": 777},
            }
        }
    )

    assert context is not None
    assert context.telegram_chat_id == "12345"
    assert context.telegram_user_id == "777"
    assert context.text == "hello"


def test_extract_message_context_ignores_unsupported_updates():
    assert extract_message_context({"callback_query": {"id": "cbq-1"}}) is None


def test_build_chat_session_id_uses_tenant_and_telegram_chat():
    assert build_chat_session_id("tenant-1", "12345") == "telegram:tenant-1:12345"
