import pytest

from personal_finance.infrastructure.database.engine import (
    create_engine_from_url,
)


def test_create_engine_from_url_uses_sqlite_connect_arguments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    sqlite_url = "sqlite:///test.db"

    captured = {}

    expected_engine = object()

    def fake_create_engine(**kwargs):
        captured.update(kwargs)

        return expected_engine

    monkeypatch.setattr(
        "personal_finance.infrastructure.database.engine.create_engine",
        fake_create_engine,
    )

    # Act
    engine = create_engine_from_url(sqlite_url)

    # Assert
    assert captured == {
        "url": sqlite_url,
        "connect_args": {
            "check_same_thread": False,
        },
    }

    assert engine is expected_engine


def test_create_engine_from_url_uses_empty_connect_arguments_for_mysql(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    mysql_url = (
        "mysql+pymysql://"
        "personal_finance_app:password@127.0.0.1:3306/personal_finance"
    )

    expected_engine = object()

    captured = {}

    def fake_create_engine(**kwargs):
        captured.update(kwargs)

        return expected_engine

    monkeypatch.setattr(
        "personal_finance.infrastructure.database.engine.create_engine",
        fake_create_engine,
    )

    # Act
    engine = create_engine_from_url(mysql_url)

    # Assert
    assert captured == {
        "url": mysql_url,
        "connect_args": {},
    }

    assert engine is expected_engine
