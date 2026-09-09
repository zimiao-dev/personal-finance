from datetime import date, datetime
from decimal import Decimal

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
)
from personal_finance.domain.entities import Transaction
from personal_finance.domain.enums import TransactionType
from personal_finance.infrastructure.database.mappers import (
    apply_replace_data_to_transaction_model,
    create_data_to_transaction_model,
    transaction_model_to_domain,
)
from personal_finance.infrastructure.database.models import TransactionModel


def test_sqlalchemy_transaction_mapper_converts_model_to_domain_transaction(
) -> None:
    # Arrange
    model = TransactionModel(
        id=123,
        amount=Decimal("18.5000"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
        created_at=datetime(2026, 9, 1, 12, 30),
    )

    # Act
    result = transaction_model_to_domain(model)

    # Assert
    assert isinstance(result, Transaction)
    assert not isinstance(result, TransactionModel)

    assert result.id == model.id
    assert result.amount == model.amount
    assert isinstance(result.amount, Decimal)

    assert result.type is TransactionType.EXPENSE
    assert result.category == model.category
    assert result.transaction_date == model.transaction_date
    assert result.description == model.description
    assert not hasattr(result, "created_at")


def test_sqlalchemy_transaction_mapper_preserves_none_description(
) -> None:
    # Arrange
    model = TransactionModel(
        id=123,
        amount=Decimal("18.5000"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 1),
        description=None,
        created_at=datetime(2026, 9, 1, 12, 30),
    )

    # Act
    result = transaction_model_to_domain(model)

    # Assert
    assert result.description is None


def test_sqlalchemy_create_data_mapper_creates_transaction_model() -> None:
    # Arrange
    data = CreateTransactionData(
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    # Act
    model = create_data_to_transaction_model(data)

    # Assert
    assert isinstance(model, TransactionModel)

    assert model.amount == data.amount
    assert model.type == data.type.value
    assert model.category == data.category
    assert model.transaction_date == data.transaction_date
    assert model.description == data.description

    assert model.id is None
    assert model.created_at is None


def test_sqlalchemy_replace_data_mapper_updates_business_fields() -> None:
    # Arrange
    model = TransactionModel(
        id=123,
        amount=Decimal("18.50"),
        type="income",
        category="transportation",
        transaction_date=date(2026, 9, 1),
        description="subway",
    )

    original_id = model.id
    original_created_at = model.created_at

    data = ReplaceTransactionData(
        amount=Decimal("20.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 9),
        description=None,
    )

    # Act
    result = apply_replace_data_to_transaction_model(model, data)

    # Assert
    assert result is None

    assert model.amount == data.amount
    assert model.type == data.type.value
    assert model.category == data.category
    assert model.transaction_date == data.transaction_date
    assert model.description == data.description

    assert model.id == original_id
    assert model.created_at == original_created_at
