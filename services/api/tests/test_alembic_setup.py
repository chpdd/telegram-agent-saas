from pathlib import Path

from alembic.config import Config


def test_alembic_config_points_to_script_location():
    config = Config(str(Path(__file__).parents[3] / "alembic.ini"))
    script_location = config.get_main_option("script_location")
    assert script_location == "alembic"

    alembic_dir = Path(__file__).parents[3] / script_location
    assert alembic_dir.exists()
    assert (alembic_dir / "versions").exists()


def test_initial_migration_exists_and_creates_core_tables():
    versions_dir = Path(__file__).parents[3] / "alembic" / "versions"
    migration = versions_dir / "20260324_0001_initial_schema.py"

    assert migration.exists()
    content = migration.read_text()

    for table_name in ["tenants", "products", "chats", "messages", "orders"]:
        assert f'"{table_name}"' in content
