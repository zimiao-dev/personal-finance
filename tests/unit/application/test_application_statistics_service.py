from datetime import date
from decimal import Decimal

import pytest

from personal_finance.application.dto import StatisticsQuery
from personal_finance.application.services.statistics_service import (
    StatisticsService,
)
from personal_finance.domain.entities import TransactionStatistics

from .fakes import FakeTransactionRepository, FakeUnitOfWork


@pytest.mark.parametrize(
    "repository_statistics",
    [
        TransactionStatistics(
            total_income=Decimal("1000.00"),
            total_expense=Decimal("400.80"),
            transaction_count=10,
        ),
        TransactionStatistics(
            total_income=Decimal("0"),
            total_expense=Decimal("0"),
            transaction_count=0,
        ),
    ],
    ids=[
        "non_zero_statistics",
        "zero_statistics",
    ],
)
def test_get_passes_query_and_returns_repository_statistics_without_committing(
    repository_statistics: TransactionStatistics,
) -> None:
    # Arrange
    query = StatisticsQuery(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 30),
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.summarize_result = repository_statistics

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = StatisticsService(uow)

    # Act
    result = service.get(query)

    # Assert
    assert result is repository_statistics

    assert len(repository.summarized_queries) == 1
    assert repository.summarized_queries[0] is query

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "summarize", "exit"]
