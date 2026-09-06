from datetime import date, datetime
from decimal import Decimal, Overflow, localcontext

import pytest

from personal_finance.domain.enums import TransactionType
from personal_finance.domain.exceptions import DomainValidationError
from personal_finance.domain.rules import (
    calculate_statistics_balance,
    normalize_category,
    normalize_description,
    validate_date_range,
    validate_statistics_total,
    validate_transaction_amount,
    validate_transaction_count,
    validate_transaction_date,
    validate_transaction_id,
    validate_transaction_type,
)


def test_validate_transaction_id_returns_positive_integer() -> None:
    # Arrange
    positive_value = 15

    # Act
    result = validate_transaction_id(positive_value)

    # Assert
    assert result == positive_value
    assert type(result) is int


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        True,
        1.0,
        "1",
        None,
    ],
    ids=[
        "zero",
        "negative_integer",
        "bool",
        "float",
        "string",
        "none",
    ],
)
def test_validate_transaction_id_rejects_invalid_value(value: object) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_id(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("0.0001"),
        Decimal("0.1"),
        Decimal("1"),
        Decimal("128.50"),
        Decimal("99999999999.9999"),
    ],
    ids=[
        "minimum",
        "one_decimal_place",
        "integer",
        "trailing_zero",
        "maximum",
    ],
)
def test_validate_transaction_amount_returns_valid_decimal(
    value: Decimal,
) -> None:
    # Act
    result = validate_transaction_amount(value)

    # Assert
    assert type(result) is Decimal
    assert result is value


@pytest.mark.parametrize(
    "value",
    [
        1,
        0.1,
        "1",
        True,
        None,
    ],
    ids=[
        "integer",
        "float",
        "string",
        "bool",
        "none",
    ],
)
def test_validate_transaction_amount_rejects_non_decimal_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_amount(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
    ids=[
        "nan",
        "infinity",
        "negative_infinity",
    ],
)
def test_validate_transaction_amount_rejects_non_finite_decimal(
    value: Decimal,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_amount(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("-0.0000"),
    ],
    ids=[
        "zero",
        "negative",
        "negative_zero",
    ],
)
def test_validate_transaction_amount_rejects_non_positive_decimal(
    value: Decimal,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_amount(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("0.00001"),
        Decimal("1.00000"),
        Decimal("99999999999.99999"),
        Decimal("100000000000"),
    ],
    ids=[
        "below_minimum",
        "too_many_decimal_places",
        "too_many_decimal_places_near_maximum",
        "above_maximum",
    ],
)
def test_validate_transaction_amount_rejects_out_of_range_decimal(
    value: Decimal,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_amount(value)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("餐饮", "餐饮"),
        ("  餐饮  ", "餐饮"),
        ("Food", "Food"),
        ("\tTravel\n", "Travel"),
        ("Food  Delivery", "Food  Delivery"),
    ],
    ids=[
        "normal_string",
        "leading_and_trailing_spaces",
        "preserve_case",
        "leading_tab_and_trailing_newline",
        "preserve_internal_spaces",
    ],
)
def test_normalize_category_returns_normalized_string(
    value: str,
    expected: str,
) -> None:
    # Act
    result = normalize_category(value)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "  ",
        "\t\n",
    ],
    ids=[
        "empty_string",
        "spaces_only",
        "whitespace_only",
    ],
)
def test_normalize_category_rejects_empty_string(value: str) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        normalize_category(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        1,
        True,
        Decimal("1"),
    ],
    ids=[
        "none",
        "integer",
        "bool",
        "decimal",
    ],
)
def test_normalize_category_rejects_non_string_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        normalize_category(value)


def test_normalize_description_returns_none_for_none() -> None:
    # Act
    result = normalize_description(None)

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "value",
    [
        "",
        "  ",
        "\t\n",
    ],
    ids=[
        "empty_string",
        "spaces_only",
        "whitespace_only",
    ],
)
def test_normalize_description_returns_none_for_empty_string(
    value: str,
) -> None:
    # Act
    result = normalize_description(value)

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "value, expected",
    [
        ("lunch", "lunch"),
        ("  lunch  ", "lunch"),
        ("Food  Delivery", "Food  Delivery"),
    ],
    ids=[
        "normal_string",
        "leading_and_trailing_spaces",
        "preserve_internal_spaces",
    ],
)
def test_normalize_description_returns_normalized_string(
    value: str,
    expected: str,
) -> None:
    # Act
    result = normalize_description(value)

    # Assert
    assert result == expected


@pytest.mark.parametrize(
    "value",
    [
        1,
        True,
        Decimal("1"),
    ],
    ids=[
        "integer",
        "bool",
        "decimal",
    ],
)
def test_normalize_description_rejects_non_string_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        normalize_description(value)


@pytest.mark.parametrize(
    "value",
    [
        TransactionType.INCOME,
        TransactionType.EXPENSE,
    ],
    ids=[
        "income",
        "expense",
    ],
)
def test_validate_transaction_type_returns_supported_type(
    value: TransactionType,
) -> None:
    # Act
    result = validate_transaction_type(value)

    # Assert
    assert result is value


@pytest.mark.parametrize(
    "value",
    [
        "income",
        "expense",
        "INCOME",
        None,
        1,
        True,
    ],
    ids=[
        "raw_income_string",
        "raw_expense_string",
        "uppercase_string",
        "none",
        "integer",
        "bool",
    ],
)
def test_validate_transaction_type_rejects_invalid_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_type(value)


@pytest.mark.parametrize(
    "value",
    [
        date(2026, 9, 1),
        date(2024, 2, 29),
    ],
    ids=[
        "normal_date",
        "leap_day",
    ],
)
def test_validate_transaction_date_returns_date(value: date) -> None:
    # Act
    result = validate_transaction_date(value)

    # Assert
    assert result is value
    assert type(result) is date


@pytest.mark.parametrize(
    "value",
    [
        "2026-09-01",
        datetime(2026, 9, 1, 0, 0),
        None,
        20260901,
        True,
    ],
    ids=[
        "string",
        "datetime",
        "none",
        "integer",
        "bool",
    ],
)
def test_validate_transaction_date_rejects_invalid_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_date(value)


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        (None, None),
        (date(2026, 9, 1), date(2026, 9, 1)),
        (date(2026, 9, 1), date(2026, 9, 30)),
    ],
    ids=[
        "no_date_range",
        "same_date",
        "forward_range",
    ],
)
def test_validate_date_range_accepts_valid_range(
    start_date: date | None,
    end_date: date | None,
) -> None:
    # Act
    result = validate_date_range(start_date, end_date)

    # Assert
    assert result is None


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        (date(2026, 9, 1), None),
        (None, date(2026, 9, 1)),
    ],
    ids=[
        "missing_end_date",
        "missing_start_date",
    ],
)
def test_validate_date_range_rejects_unpaired_dates(
    start_date: date | None,
    end_date: date | None,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_date_range(start_date, end_date)


def test_validate_date_range_rejects_start_after_end() -> None:
    # Arrange
    start_date = date(2026, 9, 30)
    end_date = date(2026, 9, 1)

    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_date_range(start_date, end_date)


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        ("2026-09-01", date(2026, 9, 30)),
        (date(2026, 9, 1), "2026-09-30"),
        (datetime(2026, 9, 1, 0, 0), date(2026, 9, 30)),
        (date(2026, 9, 1), datetime(2026, 9, 30, 0, 0)),
    ],
    ids=[
        "invalid_start_date_type",
        "invalid_end_date_type",
        "invalid_start_date_type_datetime",
        "invalid_end_date_type_datetime",
    ],
)
def test_validate_date_range_rejects_invalid_date_type(
    start_date: object,
    end_date: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_date_range(start_date, end_date)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("0"),
        Decimal("-0.0000"),
        Decimal("10.5"),
        Decimal("100000000000.0000"),
    ],
    ids=[
        "zero",
        "negative_zero",
        "positive_decimal",
        "exceeds_transaction_limit",
    ],
)
def test_validate_statistics_total_returns_non_negative_decimal(
    value: Decimal,
) -> None:
    # Act
    result = validate_statistics_total(value)

    # Assert
    assert result is value
    assert type(result) is Decimal


@pytest.mark.parametrize(
    "value",
    [
        1,
        0.1,
        "1",
        True,
        None,
    ],
    ids=[
        "integer",
        "float",
        "string",
        "bool",
        "none",
    ],
)
def test_validate_statistics_total_rejects_non_decimal_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_statistics_total(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
    ids=[
        "nan",
        "infinity",
        "negative_infinity",
    ],
)
def test_validate_statistics_total_rejects_non_finite_decimal(
    value: Decimal,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_statistics_total(value)


@pytest.mark.parametrize(
    "value",
    [
        Decimal("-0.0001"),
        Decimal("-1"),
    ],
    ids=[
        "negative_fraction",
        "negative_integer",
    ],
)
def test_validate_statistics_total_rejects_negative_decimal(
    value: Decimal,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_statistics_total(value)


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        100,
    ],
    ids=[
        "zero",
        "positive_one",
        "positive_integer",
    ],
)
def test_validate_transaction_count_returns_non_negative_integer(
    value: int,
) -> None:
    # Act
    result = validate_transaction_count(value)

    # Assert
    assert result is value
    assert type(result) is int


@pytest.mark.parametrize(
    "value",
    [
        -1,
        True,
        1.0,
        "1",
        None,
    ],
    ids=[
        "negative_integer",
        "bool",
        "float",
        "string",
        "none",
    ],
)
def test_validate_transaction_count_rejects_invalid_value(
    value: object,
) -> None:
    # Act + Assert
    with pytest.raises(DomainValidationError):
        validate_transaction_count(value)


def test_calculate_statistics_balance_rejects_overflow() -> None:
    # Arrange
    income = Decimal("1e1000000")
    expense = Decimal("0")

    # Act + Assert
    with pytest.raises(
        DomainValidationError,
        match="statistics balance must be a finite Decimal"
    ):
        calculate_statistics_balance(income, expense)


def test_calculate_statistics_balance_rejects_non_finite_result() -> None:
    # Arrange
    income = Decimal("1e1000000")
    expense = Decimal("0")

    with localcontext() as context:
        context.traps[Overflow] = False

        # Act + Assert
        with pytest.raises(
            DomainValidationError,
            match="statistics balance must be a finite Decimal",
        ):
            calculate_statistics_balance(
                income,
                expense,
            )
