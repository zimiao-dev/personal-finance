from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from personal_finance.api.app import create_app
from personal_finance.api.dependencies import get_statistics_service

from personal_finance.application.dto import StatisticsQuery
from personal_finance.domain.entities import TransactionStatistics


class FakeStatisticsService:
    def __init__(self) -> None:
        self.get_calls: list[StatisticsQuery] = []
        self.get_result: TransactionStatistics | None = None

    def get(
        self,
        query: StatisticsQuery,
    ) -> TransactionStatistics:
        self.get_calls.append(query)

        if self.get_result is None:
            raise AssertionError("get_result was not configured")

        return self.get_result


def test_get_statistics_passes_date_range_and_returns_statistics() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeStatisticsService()

    statistics = TransactionStatistics(
        total_income=Decimal("1000.00"),
        total_expense=Decimal("300.00"),
        transaction_count=5,
    )

    fake_service.get_result = statistics

    app.dependency_overrides[get_statistics_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.get(
        "/statistics"
        "?start_date=2026-09-01"
        "&end_date=2026-09-30"
    )

    # Assert
    assert response.status_code == 200

    assert response.json() == {
        "total_income": "1000.00",
        "total_expense": "300.00",
        "transaction_count": 5,
        "balance": "700.00",
    }

    assert len(fake_service.get_calls) == 1

    query = fake_service.get_calls[0]

    assert isinstance(query, StatisticsQuery)
    assert query.start_date == date(2026, 9, 1)
    assert query.end_date == date(2026, 9, 30)
