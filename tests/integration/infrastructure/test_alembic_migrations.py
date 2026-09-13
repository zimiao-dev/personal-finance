from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_alembic_upgrade_head_creates_transactions_table_in_empty_database(
    tmp_path: Path,
) -> None:
    # Arrange
    database_path = tmp_path / "migration_test.db"
    temporary_database_url = f"sqlite:///{database_path}"

    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        temporary_database_url,
    )

    # Act
    command.upgrade(
        alembic_config,
        "head",
    )

    # Assert
    assert database_path.exists()

    engine = create_engine(temporary_database_url)

    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        assert "transactions" in table_names
        assert "alembic_version" in table_names
    finally:
        engine.dispose()
