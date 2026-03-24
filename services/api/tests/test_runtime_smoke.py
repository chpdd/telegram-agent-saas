from pathlib import Path
from subprocess import run


def test_docker_compose_config_is_valid():
    project_root = Path(__file__).parents[3]
    result = run(
        ["docker", "compose", "config"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert "tca_api" in result.stdout
    assert "tca_worker" in result.stdout
    assert "tca_bot" in result.stdout
    assert "tca_admin" in result.stdout
