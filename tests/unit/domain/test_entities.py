from datetime import date
from decimal import Decimal

import pytest

from personal_finance.domain.entities import (
    Transaction,
    TransactionStatistics,
)
from personal_finance.domain.enums import TransactionType
from personal_finance.domain.exceptions import DomainValidationError


def test_transaction_stores_valid_fields() -> None:
    # Arrange
    raw_id = 15
    raw_amount = Decimal("10.80")
    raw_type = TransactionType.EXPENSE
    normal_category = "餐饮"
    raw_date = date(2026, 9, 1)
    normal_description = "lunch"

    # Act
    transaction = Transaction(
        id=raw_id,
        amount=raw_amount,
        type=raw_type,
        category=normal_category,
        transaction_date=raw_date,
        description=normal_description,
    )

    # Assert
    assert transaction.id == raw_id
    assert type(transaction.id) is int

    assert transaction.amount == raw_amount
    assert type(transaction.amount) is Decimal

    assert transaction.type is raw_type
    assert type(transaction.type) is TransactionType

    assert transaction.category == normal_category
    assert type(transaction.category) is str

    assert transaction.transaction_date == raw_date
    assert type(transaction.transaction_date) is date

    assert transaction.description == normal_description
    assert type(transaction.description) is str


def test_transaction_normalizes_category_and_description() -> None:
    # Arrange
    raw_category = "  餐饮  "
    raw_description = "  lunch  "
    normalized_category = "餐饮"
    normalized_description = "lunch"

    # Act
    transaction = Transaction(
        id=15,
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category=raw_category,
        transaction_date=date(2026, 9, 1),
        description=raw_description,
    )

    # Assert
    assert transaction.category == normalized_category
    assert transaction.description == normalized_description


@pytest.mark.parametrize(
    "description_value",
    [
        None,
        "",
        "  ",
    ],
    ids=[
        "none",
        "empty_string",
        "spaces_only",
    ],
)
def test_transaction_normalizes_empty_description_to_none(
    description_value: str | None,
) -> None:
    # Act
    transaction = Transaction(
        id=15,
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="餐饮",
        transaction_date=date(2026, 9, 1),
        description=description_value,
    )

    # Assert
    assert transaction.description is None


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("id", 0),
        ("amount", Decimal("0")),
        ("type", "income"),
        ("category", " "),
        ("transaction_date", "2026-09-01"),
        ("description", 1),
    ],
    ids=[
        "id_zero",
        "amount_zero",
        "type_string",
        "category_blank",
        "transaction_date_string",
        "description_integer",
    ],
)
def test_transaction_rejects_invalid_field(
    field: str,
    invalid_value: object,
) -> None:
    # Arrange
    params = {
        "id": 1,
        "amount": Decimal("100.0"),
        "type": TransactionType.INCOME,
        "category": "salary",
        "transaction_date": date(2026, 9, 1),
        "description": None,
    }

    params[field] = invalid_value

    # Act + Assert
    with pytest.raises(DomainValidationError):
        Transaction(**params)


def test_transaction_defaults_description_to_none() -> None:
    # Act
    transaction = Transaction(
        id=15,
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="餐饮",
        transaction_date=date(2026, 9, 1),
    )

    # Assert
    assert transaction.description is None


def test_transaction_statistics_calculates_positive_balance() -> None:
    # Arrange
    income = Decimal("100.5")
    expense = Decimal("30")
    count = 10
    balance = Decimal("70.5")

    # Act
    transaction_statistics = TransactionStatistics(
        total_income=income,
        total_expense=expense,
        transaction_count=count,
    )

    # Assert
    assert transaction_statistics.total_income == income
    assert type(transaction_statistics.total_income) is Decimal

    assert transaction_statistics.total_expense == expense
    assert type(transaction_statistics.total_expense) is Decimal

    assert transaction_statistics.transaction_count == count
    assert type(transaction_statistics.transaction_count) is int

    assert transaction_statistics.balance == balance
    assert type(transaction_statistics.balance) is Decimal


def test_transaction_statistics_represents_empty_statistics() -> None:
    # Arrange
    income = Decimal("0")
    expense = Decimal("0")
    count = 0
    balance = Decimal("0")

    # Act
    transaction_statistics = TransactionStatistics()

    # Assert
    assert transaction_statistics.total_income == income
    assert transaction_statistics.total_expense == expense
    assert transaction_statistics.transaction_count == count
    assert transaction_statistics.balance == balance


def test_transaction_statistics_calculates_negative_balance() -> None:
    # Arrange
    income = Decimal("10")
    expense = Decimal("30.5")
    count = 10
    balance = Decimal("-20.5")

    # Act
    transaction_statistics = TransactionStatistics(
        total_income=income,
        total_expense=expense,
        transaction_count=count,
    )

    # Assert
    assert transaction_statistics.total_income == income
    assert type(transaction_statistics.total_income) is Decimal

    assert transaction_statistics.total_expense == expense
    assert type(transaction_statistics.total_expense) is Decimal

    assert transaction_statistics.transaction_count == count
    assert type(transaction_statistics.transaction_count) is int

    assert transaction_statistics.balance == balance
    assert type(transaction_statistics.balance) is Decimal


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("total_income", Decimal("-1")),
        ("total_expense", Decimal("NaN")),
        ("transaction_count", -1),
    ],
    ids=[
        "total_income_negative",
        "total_expense_nan",
        "transaction_count_negative",
    ],
)
def test_transaction_statistics_rejects_invalid_field(
    field: str,
    invalid_value: object,
) -> None:
    # Arrange
    params = {
        "total_income": Decimal("100.5"),
        "total_expense": Decimal("30"),
        "transaction_count": 10,
    }

    params[field] = invalid_value

    # Act + Assert
    with pytest.raises(DomainValidationError):
        TransactionStatistics(**params)


def test_transaction_statistics_rejects_unrepresentable_balance() -> None:
    # Arrange
    income = Decimal("1e1000000")
    expense = Decimal("0")
    count = 10

    # Act + Assert
    with pytest.raises(DomainValidationError):
        TransactionStatistics(
            total_income=income,
            total_expense=expense,
            transaction_count=count,
        )
