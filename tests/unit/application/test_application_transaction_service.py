from datetime import date
from decimal import Decimal
from typing import Never

import pytest

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    TransactionQuery,
)
from personal_finance.application.exceptions import TransactionNotFoundError
from personal_finance.application.services.transaction_service import (
    TransactionService,
)
from personal_finance.domain.entities import Transaction
from personal_finance.domain.exceptions import DomainValidationError
from personal_finance.domain.enums import TransactionType

from .fakes import FakeTransactionRepository, FakeUnitOfWork


class FailingAddTransactionRepository(FakeTransactionRepository):
    def __init__(
        self,
        repository_error: RuntimeError,
        events: list[str],
    ) -> None:
        super().__init__(events)
        self.repository_error = repository_error

    def add(self, data: CreateTransactionData) -> Never:
        self.added_data.append(data)
        self.events.append("add")
        raise self.repository_error


def test_create_commits_and_returns_repository_transaction() -> None:
    # Arrange
    create_data = CreateTransactionData(
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food Delivery",
        transaction_date=date(2026, 9, 1),
        description="dinner with friends",
    )

    repository_transaction = Transaction(
        id=1,
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food Delivery",
        transaction_date=date(2026, 9, 1),
        description="dinner with friends",
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.add_result = repository_transaction

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act
    result = service.create(create_data)

    # Assert
    assert len(repository.added_data) == 1
    assert repository.added_data[0] is create_data

    assert result is repository_transaction

    assert uow.enter_count == 1
    assert uow.commit_count == 1
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "add", "commit", "exit"]


def test_create_propagates_error_without_committing() -> None:
    # Arrange
    create_data = CreateTransactionData(
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food Delivery",
        transaction_date=date(2026, 9, 1),
        description="dinner with friends",
    )

    repository_error: RuntimeError = RuntimeError(
        "repository create sentinel failure",
    )

    events: list[str] = []

    repository = FailingAddTransactionRepository(
        repository_error=repository_error,
        events=events,
    )

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act + Assert
    with pytest.raises(RuntimeError) as exc_info:
        service.create(create_data)

    assert exc_info.value is repository_error
    assert len(repository.added_data) == 1
    assert repository.added_data[0] is create_data

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 1
    assert uow.exit_count == 1
    assert uow.exit_exception_type is RuntimeError

    assert events == ["enter", "add", "rollback", "exit"]


def test_get_returns_transaction_without_committing() -> None:
    # Arrange
    transaction_id = 123

    repository_transaction = Transaction(
        id=transaction_id,
        amount=Decimal("100.00"),
        type=TransactionType.INCOME,
        category="salary",
        transaction_date=date(2026, 9, 1),
        description=None,
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.get_result = repository_transaction

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act
    result = service.get(transaction_id)

    # Assert
    assert result is repository_transaction

    assert len(repository.gotten_ids) == 1
    assert repository.gotten_ids[0] == transaction_id

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "get", "exit"]


def test_get_raises_transaction_not_found_without_committing() -> None:
    # Arrange
    transaction_id = 15

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.get_result = None

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act + Assert
    with pytest.raises(
        TransactionNotFoundError,
        match=f"transaction {transaction_id} was not found",
    ):
        service.get(transaction_id)

    assert len(repository.gotten_ids) == 1
    assert repository.gotten_ids[0] == transaction_id

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 1
    assert uow.exit_count == 1
    assert uow.exit_exception_type is TransactionNotFoundError

    assert events == ["enter", "get", "rollback", "exit"]


def test_get_rejects_invalid_id_before_entering_unit_of_work() -> None:
    # Arrange
    transaction_id = 0

    events: list[str] = []

    repository_transaction = Transaction(
        id=1,
        amount=Decimal("100.00"),
        type=TransactionType.INCOME,
        category="salary",
        transaction_date=date(2026, 9, 1),
        description=None,
    )

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.get_result = repository_transaction

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act + Assert
    with pytest.raises(DomainValidationError):
        service.get(transaction_id)

    assert len(repository.gotten_ids) == 0

    assert uow.enter_count == 0
    assert uow.commit_count == 0
    assert uow.rollback_count == 0
    assert uow.exit_count == 0
    assert uow.exit_exception_type is None

    assert events == []


@pytest.mark.parametrize(
    "repository_transactions",
    [
        [],
        [
            Transaction(
                id=1,
                amount=Decimal("18.50"),
                type=TransactionType.EXPENSE,
                category="Food",
                transaction_date=date(2026, 9, 1),
                description="dinner",
            ),
            Transaction(
                id=2,
                amount=Decimal("100.0"),
                type=TransactionType.INCOME,
                category="Food",
                transaction_date=date(2026, 9, 7),
                description="餐补",
            ),
        ],
    ],
    ids=[
        "empty_result",
        "non_empty_result",
    ],
)
def test_list_passes_query_and_returns_repository_list_without_committing(
    repository_transactions: list[Transaction],
) -> None:
    # Arrange
    query = TransactionQuery(
        category="Food",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 15),
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.list_result = repository_transactions

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act
    result = service.list(query)

    # Assert
    assert len(repository.listed_queries) == 1
    assert repository.listed_queries[0] is query

    assert result is repository_transactions

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "list", "exit"]


def test_replace_commits_and_returns_repository_transaction() -> None:
    # Arrange
    transaction_id = 123

    replace_data = ReplaceTransactionData(
        amount=Decimal("10.0"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 6),
        description="dinner",
    )

    repository_transaction = Transaction(
        id=transaction_id,
        amount=Decimal("10.0"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 6),
        description="dinner",
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )

    repository.replace_result = repository_transaction

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act
    result = service.replace(transaction_id, replace_data)

    # Assert
    assert len(repository.replaced_arguments) == 1

    replaced_id, replaced_data = repository.replaced_arguments[0]

    assert replaced_id == transaction_id
    assert replaced_data is replace_data

    assert result is repository_transaction

    assert uow.enter_count == 1
    assert uow.commit_count == 1
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "replace", "commit", "exit"]


def test_replace_raises_transaction_not_found_without_committing() -> None:
    # Arrange
    transaction_id = 15

    replace_data = ReplaceTransactionData(
        amount=Decimal("10.0"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 6),
        description="dinner",
    )

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.replace_result = None

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act + Assert
    with pytest.raises(
        TransactionNotFoundError,
        match=f"transaction {transaction_id} was not found",
    ):
        service.replace(transaction_id, replace_data)

    assert len(repository.replaced_arguments) == 1

    replaced_id, replaced_data = repository.replaced_arguments[0]

    assert replaced_id == transaction_id
    assert replaced_data is replace_data

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 1
    assert uow.exit_count == 1
    assert uow.exit_exception_type is TransactionNotFoundError

    assert events == ["enter", "replace", "rollback", "exit"]


def test_delete_commits_when_repository_reports_success() -> None:
    # Arrange
    transaction_id = 123

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.delete_result = True

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act
    result = service.delete(transaction_id)

    # Assert
    assert result is None

    assert len(repository.deleted_ids) == 1
    assert repository.deleted_ids[0] == transaction_id

    assert uow.enter_count == 1
    assert uow.commit_count == 1
    assert uow.rollback_count == 0
    assert uow.exit_count == 1
    assert uow.exit_exception_type is None

    assert events == ["enter", "delete", "commit", "exit"]


def test_delete_raises_transaction_not_found_without_committing() -> None:
    # Arrange
    transaction_id = 15

    events: list[str] = []

    repository = FakeTransactionRepository(
        events=events,
    )
    repository.delete_result = False

    uow = FakeUnitOfWork(
        transactions=repository,
        events=events,
    )

    service = TransactionService(uow)

    # Act + Assert
    with pytest.raises(
        TransactionNotFoundError,
        match=f"transaction {transaction_id} was not found",
    ):
        service.delete(transaction_id)

    assert len(repository.deleted_ids) == 1
    assert repository.deleted_ids[0] == transaction_id

    assert uow.enter_count == 1
    assert uow.commit_count == 0
    assert uow.rollback_count == 1
    assert uow.exit_count == 1
    assert uow.exit_exception_type is TransactionNotFoundError

    assert events == ["enter", "delete", "rollback", "exit"]
