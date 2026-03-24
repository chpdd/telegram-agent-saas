from pathlib import Path

ROOT = Path(__file__).parents[3]


def test_ci_workflow_runs_quality_gates():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "uv run ruff check ." in workflow
    assert "uv run pytest" in workflow
    assert "docker compose config" in workflow
    assert "pull_request:" in workflow


def test_cd_workflow_publishes_images_to_ghcr():
    workflow = (ROOT / ".github" / "workflows" / "cd.yml").read_text(encoding="utf-8")

    assert "ghcr.io/${{ github.repository }}" in workflow
    assert "docker/login-action@v3" in workflow
    assert "docker/build-push-action@v6" in workflow
    assert "publish-images" in workflow
