from personal_finance.api.dependencies import (
    get_statistics_service,
    get_transaction_service,
)
from personal_finance.application.services.statistics_service import (
    StatisticsService,
)
from personal_finance.application.services.transaction_service import (
    TransactionService,
)


def test_api_dependency_providers_return_services_with_separate_units_of_work(
) -> None:
    # Act
    transaction_service1 = get_transaction_service()
    transaction_service2 = get_transaction_service()
    statistics_service = get_statistics_service()

    # Assert
    assert isinstance(transaction_service1, TransactionService)
    assert isinstance(transaction_service2, TransactionService)
    assert isinstance(statistics_service, StatisticsService)

    assert transaction_service1 is not transaction_service2

    assert transaction_service1._uow is not transaction_service2._uow
    assert statistics_service._uow is not transaction_service1._uow
    assert statistics_service._uow is not transaction_service2._uow
