import sys
from collections import defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).parents[1] / "src"))

from auth import AUTH_STATUS_KEY, TENANT_ID_KEY, apply_auth, normalize_tenant_id  # noqa: E402


def test_normalize_tenant_id():
    assert normalize_tenant_id(None) == ""
    assert normalize_tenant_id("") == ""
    assert normalize_tenant_id("  shop-123 ") == "shop-123"


def test_apply_auth_updates_session():
    session = defaultdict(lambda: None)

    assert apply_auth(session, "shop-1") is True
    assert session[TENANT_ID_KEY] == "shop-1"
    assert session[AUTH_STATUS_KEY] is True


def test_apply_auth_rejects_empty():
    session = {}
    assert apply_auth(session, "") is False
    assert AUTH_STATUS_KEY not in session
