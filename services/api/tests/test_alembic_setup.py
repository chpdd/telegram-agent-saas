from pathlib import Path

from alembic.config import Config


def test_alembic_config_points_to_script_location():
    config = Config(str(Path(__file__).parents[3] / "alembic.ini"))
    script_location = config.get_main_option("script_location")
    assert script_location == "alembic"

    alembic_dir = Path(__file__).parents[3] / script_location
    assert alembic_dir.exists()
    assert (alembic_dir / "versions").exists()
