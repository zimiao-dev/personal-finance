from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from personal_finance.api.app import create_app
from personal_finance.api.dependencies import get_transaction_service
from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    TransactionQuery,
)
from personal_finance.application.exceptions import (
    TransactionNotFoundError,
)
from personal_finance.domain.exceptions import DomainValidationError
from personal_finance.domain.entities import Transaction
from personal_finance.domain.enums import TransactionType




class FakeTransactionService:
    def __init__(self) -> None:
        self.create_calls: list[CreateTransactionData] = []
        self.list_calls: list[TransactionQuery] = []
        self.get_calls: list[int] = []
        self.replace_calls: list[
            tuple[int, ReplaceTransactionData]
        ] = []
        self.delete_calls: list[int] = []

        self.create_result: Transaction | None = None
        self.list_result: list[Transaction] = []
        self.get_result: Transaction | None = None
        self.replace_result: Transaction | None = None

        self.get_error: Exception | None = None
        self.list_error: Exception | None = None

    def create(
        self,
        data: CreateTransactionData,
    ) -> Transaction:
        self.create_calls.append(data)

        if self.create_result is None:
            raise AssertionError("create_result was not configured")

        return self.create_result

    def list(
        self,
        query: TransactionQuery,
    ) -> list[Transaction]:
        self.list_calls.append(query)

        if self.list_error is not None:
            raise self.list_error

        return self.list_result

    def get(
        self,
        transaction_id: int,
    ) -> Transaction:
        self.get_calls.append(transaction_id)

        if self.get_error is not None:
            raise self.get_error

        if self.get_result is None:
            raise AssertionError("get_result was not configured")

        return self.get_result

    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction:
        self.replace_calls.append(
            (
                transaction_id,
                data,
            ),
        )

        if self.replace_result is None:
            raise AssertionError("replace_result was not configured")

        return self.replace_result

    def delete(
        self,
        transaction_id: int,
    ) -> None:
        self.delete_calls.append(transaction_id)


def test_create_transaction_returns_created_transaction() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    transaction = Transaction(
        id=42,
        amount=Decimal("100.00"),
        type=TransactionType.INCOME,
        category="Salary",
        transaction_date=date(2026, 9, 13),
        description="September salary",
    )

    fake_service.create_result = transaction

    app.dependency_overrides[get_transaction_service] = lambda: fake_service

    client = TestClient(app)

    # Act
    response = client.post(
        "/transactions",
        json={
            "amount": "100.00",
            "type": "income",
            "category": "Salary",
            "transaction_date": "2026-09-13",
            "description": "September salary",
        },
    )

    # Assert
    assert response.status_code == 201

    assert response.json() == {
        "id": 42,
        "amount": "100.00",
        "type": "income",
        "category": "Salary",
        "transaction_date": "2026-09-13",
        "description": "September salary",
    }

    assert len(fake_service.create_calls) == 1

    data = fake_service.create_calls[0]

    assert isinstance(data, CreateTransactionData)

    assert data.amount == Decimal("100.00")
    assert data.type is TransactionType.INCOME
    assert data.category == "Salary"
    assert data.transaction_date == date(2026, 9, 13)
    assert data.description == "September salary"


def test_list_transactions_passes_query_and_returns_transactions() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    transaction_1 = Transaction(
        id=1,
        amount=Decimal("20.00"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 5),
        description="Lunch",
    )

    transaction_2 = Transaction(
        id=2,
        amount=Decimal("30.00"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 10),
        description="Dinner",
    )

    fake_service.list_result = [
        transaction_1,
        transaction_2,
    ]

    app.dependency_overrides[get_transaction_service] = lambda: fake_service

    client = TestClient(app)

    # Act
    response = client.get(
        "/transactions"
        "?category=Food"
        "&start_date=2026-09-01"
        "&end_date=2026-09-30"
    )

    # Assert
    assert response.status_code == 200

    body = response.json()

    assert len(body) == 2
    assert body[0]["id"] == 1
    assert body[1]["id"] == 2

    assert len(fake_service.list_calls) == 1

    query = fake_service.list_calls[0]

    assert isinstance(query, TransactionQuery)
    assert query.category == "Food"
    assert query.start_date == date(2026, 9, 1)
    assert query.end_date == date(2026, 9, 30)


def test_get_transaction_passes_id_and_returns_transaction() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    transaction = Transaction(
        id=42,
        amount=Decimal("50.00"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 13),
        description="Dinner",
    )

    fake_service.get_result = transaction

    app.dependency_overrides[get_transaction_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.get("/transactions/42")

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == 42

    assert fake_service.get_calls == [42]


def test_replace_transaction_passes_id_and_data() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    transaction = Transaction(
        id=42,
        amount=Decimal("80.00"),
        type=TransactionType.EXPENSE,
        category="Transport",
        transaction_date=date(2026, 9, 13),
        description=None,
    )

    fake_service.replace_result = transaction

    app.dependency_overrides[get_transaction_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.put(
        "/transactions/42",
        json={
            "amount": "80.00",
            "type": "expense",
            "category": "Transport",
            "transaction_date": "2026-09-13",
            "description": None,
        },
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["id"] == 42

    assert len(fake_service.replace_calls) == 1

    transaction_id, data = fake_service.replace_calls[0]

    assert transaction_id == 42
    assert isinstance(data, ReplaceTransactionData)

    assert data.amount == Decimal("80.00")
    assert data.type is TransactionType.EXPENSE
    assert data.category == "Transport"
    assert data.transaction_date == date(2026, 9, 13)
    assert data.description is None


def test_delete_transaction_passes_id_and_returns_no_content() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    app.dependency_overrides[get_transaction_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.delete("/transactions/42")

    # Assert
    assert response.status_code == 204
    assert response.content == b""
    assert fake_service.delete_calls == [42]


def test_get_transaction_returns_404_when_transaction_is_missing() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    fake_service.get_error = TransactionNotFoundError(
        "expected API not-found sentinel",
    )

    app.dependency_overrides[get_transaction_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.get("/transactions/999")

    # Assert
    assert response.status_code == 404

    assert response.json() == {
        "detail": "expected API not-found sentinel",
    }

    assert fake_service.get_calls == [999]


def test_transaction_endpoint_returns_422_for_domain_validation_error() -> None:
    # Arrange
    app = create_app()

    fake_service = FakeTransactionService()

    fake_service.list_error = DomainValidationError(
        "expected API domain validation sentinel",
    )

    app.dependency_overrides[get_transaction_service] = (
        lambda: fake_service
    )

    client = TestClient(app)

    # Act
    response = client.get("/transactions")

    # Assert
    assert response.status_code == 422

    assert response.json() == {
        "detail": "expected API domain validation sentinel",
    }

    assert len(fake_service.list_calls) == 1
