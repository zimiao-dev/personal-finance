import pytest

from personal_finance.config import Settings


def test_settings_uses_default_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Act
    settings = Settings()

    # Assert
    assert settings.database_url == "sqlite:///data/finance_v2.db"


def test_settings_reads_database_url_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    test_url = "sqlite:///data/test_override.db"
    monkeypatch.setenv("DATABASE_URL", test_url)

    # Act
    settings = Settings()

    # Assert
    assert settings.database_url == test_url
