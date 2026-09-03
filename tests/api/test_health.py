from fastapi.testclient import TestClient

from personal_finance.api.app import create_app


def test_health_returns_ok_response() -> None:
    # Arrange
    app = create_app()
    test_client = TestClient(app)

    # Act
    response = test_client.get("/health")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["content-type"] == "application/json"
