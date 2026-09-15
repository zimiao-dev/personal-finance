import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, text
from sqlalchemy.engine import make_url

from personal_finance.infrastructure.database.engine import (
    create_engine_from_url,
)


def get_mysql_test_database_url() -> str:
    database_url = os.getenv("MYSQL_TEST_DATABASE_URL")

    if not database_url:
        pytest.skip(
            "MYSQL_TEST_DATABASE_URL is not configured"
        )

    url = make_url(database_url)

    if url.get_backend_name() != "mysql":
        pytest.fail(
            "MYSQL_TEST_DATABASE_URL must use a MySQL backend"
        )

    if not url.database or not url.database.endswith("_test"):
        pytest.fail(
            "MYSQL_TEST_DATABASE_URL must point to a database "
            "whose name ends with '_test'"
        )

    return database_url


def drop_mysql_test_tables(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(
            text("DROP TABLE IF EXISTS transactions")
        )
        connection.execute(
            text("DROP TABLE IF EXISTS alembic_version")
        )



def test_alembic_upgrade_head_creates_schema_in_empty_mysql_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    database_url = get_mysql_test_database_url()

    monkeypatch.delenv(
        "DATABASE_URL",
        raising=False,
    )

    engine = create_engine_from_url(database_url)

    try:
        drop_mysql_test_tables(engine)

        alembic_config = Config("alembic.ini")

        alembic_database_url = database_url.replace(
            "%",
            "%%",
        )

        alembic_config.set_main_option(
            "sqlalchemy.url",
            alembic_database_url,
        )

        # Act
        command.upgrade(
            alembic_config,
            "head",
        )

        # Assert
        inspector = inspect(engine)
        table_names = inspector.get_table_names()

        assert "transactions" in table_names
        assert "alembic_version" in table_names

        drop_mysql_test_tables(engine)

    finally:
        engine.dispose()
