from datetime import date
from decimal import Decimal

import pytest

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    StatisticsQuery,
    TransactionQuery,
)
from personal_finance.domain.enums import TransactionType
from personal_finance.domain.exceptions import DomainValidationError


def test_create_transaction_data_normalizes_category_and_description() -> None:
    # Arrange
    raw_amount = Decimal("128.50")
    raw_type = TransactionType.EXPENSE
    raw_category = "  Food  Delivery  "
    raw_date = date(2026, 9, 1)
    raw_description = " dinner with friends "

    normalized_category = "Food  Delivery"
    normalized_description = "dinner with friends"

    # Act
    create_transaction_data = CreateTransactionData(
        amount=raw_amount,
        type=raw_type,
        category=raw_category,
        transaction_date=raw_date,
        description=raw_description,
    )

    # Assert
    assert not hasattr(create_transaction_data, "id")
    assert create_transaction_data.amount is raw_amount
    assert create_transaction_data.type is raw_type
    assert create_transaction_data.category == normalized_category
    assert create_transaction_data.transaction_date is raw_date
    assert create_transaction_data.description == normalized_description


def test_create_transaction_data_defaults_description_to_none() -> None:
    # Arrange + Act
    create_transaction_data = CreateTransactionData(
        amount=Decimal("128.50"),
        type=TransactionType.EXPENSE,
        category="Food Delivery",
        transaction_date=date(2026, 9, 1),
    )

    # Assert
    assert create_transaction_data.description is None


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("amount", Decimal("0")),
        ("category", ""),
        ("transaction_date", "2026-09-01"),
    ],
    ids=[
        "amount_zero",
        "category_empty_string",
        "transaction_date_string",
    ],
)
def test_create_transaction_data_rejects_representative_invalid_field(
    field: str,
    invalid_value: object,
) -> None:
    # Arrange
    params = {
        "amount": Decimal("128.50"),
        "type": TransactionType.EXPENSE,
        "category": "Food Delivery",
        "transaction_date": date(2026, 9, 1),
        "description": "dinner with friends",
    }

    params[field] = invalid_value

    # Act + Assert
    with pytest.raises(DomainValidationError):
        CreateTransactionData(**params)


def test_replace_transaction_data_normalizes_category_and_description() -> None:
    # Arrange
    raw_amount = Decimal("120.80")
    raw_type = TransactionType.EXPENSE
    raw_category = "  Food  Delivery  "
    raw_date = date(2026, 9, 1)
    raw_description = "  dinner with friends  "

    normalized_category = "Food  Delivery"
    normalized_description = "dinner with friends"

    # Act
    replace_transaction_data = ReplaceTransactionData(
        amount=raw_amount,
        type=raw_type,
        category=raw_category,
        transaction_date=raw_date,
        description=raw_description,
    )

    # Assert
    assert not hasattr(replace_transaction_data, "id")
    assert replace_transaction_data.amount is raw_amount
    assert replace_transaction_data.type is raw_type
    assert replace_transaction_data.category == normalized_category
    assert replace_transaction_data.transaction_date is raw_date
    assert replace_transaction_data.description == normalized_description


def test_replace_transaction_data_accepts_explicit_none_description() -> None:
    # Arrange
    raw_description = None

    # Act
    replace_transaction_data = ReplaceTransactionData(
        amount=Decimal("120.80"),
        type=TransactionType.EXPENSE,
        category="Food Delivery",
        transaction_date=date(2026, 9, 1),
        description=raw_description,
    )

    # Assert
    assert replace_transaction_data.description is None


def test_replace_transaction_data_requires_description() -> None:
    # Arrange + Act + Assert
    with pytest.raises(TypeError):
        ReplaceTransactionData(
            amount=Decimal("120.80"),
            type=TransactionType.EXPENSE,
            category="Food Delivery",
            transaction_date=date(2026, 9, 1),
        )


@pytest.mark.parametrize(
    "field, invalid_value",
    [
        ("amount", Decimal("0")),
        ("category", ""),
        ("transaction_date", "2026-09-01"),
    ],
    ids=[
        "amount_zero",
        "category_empty_string",
        "transaction_date_string",
    ],
)
def test_replace_transaction_data_rejects_representative_invalid_field(
    field: str,
    invalid_value: object,
) -> None:
    # Arrange
    params = {
        "amount": Decimal("120.80"),
        "type": TransactionType.EXPENSE,
        "category": "Food Delivery",
        "transaction_date": date(2026, 9, 1),
        "description": "dinner with friends",
    }

    params[field] = invalid_value

    # Act + Assert
    with pytest.raises(DomainValidationError):
        ReplaceTransactionData(**params)


def test_transaction_query_defaults_to_no_filters() -> None:
    # Act
    transaction_query = TransactionQuery()

    # Assert
    assert transaction_query.category is None
    assert transaction_query.start_date is None
    assert transaction_query.end_date is None


def test_transaction_query_normalizes_category_and_preserves_date_range() -> None:
    # Arrange
    raw_category = " Food Delivery "
    raw_start_date = date(2026, 9, 1)
    raw_end_date = date(2026, 9, 30)

    normalized_category = "Food Delivery"

    # Act
    transaction_query = TransactionQuery(
        category=raw_category,
        start_date=raw_start_date,
        end_date=raw_end_date,
    )

    # Assert
    assert transaction_query.category == normalized_category
    assert transaction_query.start_date is raw_start_date
    assert transaction_query.end_date is raw_end_date


def test_transaction_query_rejects_blank_category() -> None:
    # Arrange
    raw_category = "  "

    # Act + Assert
    with pytest.raises(DomainValidationError):
        TransactionQuery(
            category=raw_category,
        )


@pytest.mark.parametrize(
    "raw_start_date, raw_end_date",
    [
        (date(2026, 9, 1), None),
        (None, date(2026, 9, 30)),
        (date(2026, 9, 30), date(2026, 9, 1)),
    ],
    ids=[
        "missing_end_date",
        "missing_start_date",
        "reversed_date_range",
    ],
)
def test_transaction_query_rejects_invalid_date_range(
    raw_start_date: date | None,
    raw_end_date: date | None,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        TransactionQuery(
            start_date=raw_start_date,
            end_date=raw_end_date,
        )


def test_statistics_query_defaults_to_no_date_range() -> None:
    # Act
    statistics_query = StatisticsQuery()

    # Assert
    assert statistics_query.start_date is None
    assert statistics_query.end_date is None


def test_statistics_query_preserves_valid_date_range() -> None:
    # Arrange
    raw_start_date = date(2026, 9, 1)
    raw_end_date = date(2026, 9, 30)

    # Act
    statistics_query = StatisticsQuery(
        start_date=raw_start_date,
        end_date=raw_end_date,
    )

    # Assert
    assert statistics_query.start_date is raw_start_date
    assert statistics_query.end_date is raw_end_date


@pytest.mark.parametrize(
    "raw_start_date, raw_end_date",
    [
        (date(2026, 9, 1), None),
        (None, date(2026, 9, 30)),
        (date(2026, 9, 30), date(2026, 9, 1)),
    ],
    ids=[
        "missing_end_date",
        "missing_start_date",
        "reversed_date_range",
    ],
)
def test_statistics_query_rejects_invalid_date_range(
    raw_start_date: date | None,
    raw_end_date: date | None,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        StatisticsQuery(
            start_date=raw_start_date,
            end_date=raw_end_date,
        )
