import os
import sys
from pathlib import Path

os.environ.setdefault("LLM_API_KEY", "test")

API_SRC = str(Path(__file__).parents[1] / "src")
if API_SRC in sys.path:
    sys.path.remove(API_SRC)
sys.path.insert(0, API_SRC)

for module_name in ["main", "core", "core.config", "core.logging"]:
    sys.modules.pop(module_name, None)

from fastapi.testclient import TestClient  # noqa: E402

from main import create_app  # noqa: E402


def test_create_app_exposes_healthcheck():
    with TestClient(create_app()) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "api",
        "mode": "DEV",
    }


def test_create_app_stores_settings_on_state():
    app = create_app()

    with TestClient(app):
        assert app.state.settings.LLM_API_KEY == os.environ["LLM_API_KEY"]
