from fastapi import FastAPI

from personal_finance.api.app import create_app


def test_create_app_returns_configured_fastapi_instance() -> None:
    # Arrange + Act
    app = create_app()

    # Assert
    assert isinstance(app, FastAPI)
    assert app.title == "Personal Finance API"
    assert app.version == "0.2.0"


def test_create_app_returns_new_instance() -> None:
    # Arrange + Act
    first_app = create_app()
    second_app = create_app()

    # Assert
    assert first_app is not second_app
