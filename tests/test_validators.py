import pytest

from validators import (
    validate_amount,
    validate_date,
    validate_type,
    validate_id,
    validate_category,
    validate_date_range,
)


@pytest.mark.parametrize(
    "amount_input, expected_amount",
    [
        ("100", 100.0),
        ("100.5", 100.5),
        ("  88.6  ", 88.6),
    ],
    ids=[
        "positive_integer",
        "positive_decimal",
        "surrounding_whitespace",
    ],
)
def test_validate_amount_returns_float_for_valid_input(
    amount_input,
    expected_amount,
):
    result = validate_amount(amount_input)

    assert result == expected_amount


def test_validate_amount_rejects_zero():
    with pytest.raises(ValueError, match="金额必须大于0"):
        validate_amount("0")


@pytest.mark.parametrize(
    "amount_input",
    ["-1", "-100.5", "abc", "", "   ", None],
    ids=[
        "negative_integer",
        "negative_decimal",
        "non_numeric",
        "empty_string",
        "whitespace_only",
        "none",
    ],
)
def test_validate_amount_rejects_invalid_input(amount_input):
    with pytest.raises(ValueError):
        validate_amount(amount_input)


@pytest.mark.parametrize(
    "non_finite_amount",
    ["nan", "inf", "-inf"],
    ids=[
        "not_a_number",
        "positive_infinity",
        "negative_infinity",
    ],
)
def test_validate_amount_rejects_non_finite_input(non_finite_amount):
    with pytest.raises(ValueError, match="金额必须是有限数字"):
        validate_amount(non_finite_amount)


@pytest.mark.parametrize(
    "date_input, expected_date",
    [
        ("2026-08-21", "2026-08-21"),
        ("  2026-08-21  ", "2026-08-21"),
        ("2024-02-29", "2024-02-29"),
    ],
    ids=[
        "valid_date",
        "surrounding_whitespace",
        "leap_year_date",
    ],
)
def test_validate_date_returns_normalized_valid_date(date_input, expected_date):
    result = validate_date(date_input)

    assert result == expected_date


@pytest.mark.parametrize(
    "date_input",
    [
        "2026-8-21",
        "2026-08-1",
        "2026/08/21",
        "21-08-2026",
        "2026-13-01",
        "2026-02-29",
        "",
        "    ",
        None,
    ],
    ids=[
        "month_without_zero_padding",
        "day_without_zero_padding",
        "slash_separator",
        "day_first_order",
        "month_out_of_range",
        "non_leap_year_feb_29",
        "empty_string",
        "whitespace_only",
        "none",
    ],
)
def test_validate_date_rejects_invalid_input(date_input):
    with pytest.raises(
        ValueError,
        match="日期格式错误，应为 YYYY-MM-DD",
    ):
        validate_date(date_input)


@pytest.mark.parametrize(
    "type_input, expected_type",
    [
        ("income", "income"),
        ("expense", "expense"),
    ],
    ids=[
        "income",
        "expense",
    ],
)
def test_validate_type_returns_valid_type_for_standard_input(
    type_input,
    expected_type,
):
    result = validate_type(type_input)

    assert result == expected_type


@pytest.mark.parametrize(
    "type_input, expected_type",
    [
        ("  income  ", "income"),
        ("Expense", "expense"),
        ("  INCOME  ", "income"),
    ],
    ids=[
        "income_surrounding_whitespace",
        "expense_mixed_case",
        "income_uppercase_with_whitespace",
    ],
)
def test_validate_type_normalizes_valid_input(type_input, expected_type):
    result = validate_type(type_input)

    assert result == expected_type


@pytest.mark.parametrize(
    "type_input",
    [
        "",
        "    ",
        "salary",
        "incomes",
        None,
        "10",
        12,
    ],
    ids=[
        "empty_string",
        "whitespace_only",
        "unsupported_type",
        "income_with_suffix",
        "none",
        "numeric_string",
        "integer",
    ],
)
def test_validate_type_rejects_invalid_input(type_input):
    with pytest.raises(ValueError, match="类型必须是income或expense"):
        validate_type(type_input)


@pytest.mark.parametrize(
    "id_input, expected_id",
    [
        ("10", 10),
    ],
    ids=[
        "positive_integer",
    ],
)
def test_validate_id_returns_valid_id_for_standard_input(
    id_input, 
    expected_id,
):
    result = validate_id(id_input)

    assert result == expected_id
    assert type(result) is int


@pytest.mark.parametrize(
    "id_input, expected_id",
    [
        ("  12  ", 12),
        ("0012", 12),
        ("+12", 12),
    ],
    ids=[
        "integer_surrounding_whitespace",
        "integer_with_leading_zeros",
        "integer_with_a_plus_sign",
    ],
)
def test_validate_id_normalizes_valid_input(
    id_input, 
    expected_id,
):
    result = validate_id(id_input)

    assert result == expected_id


@pytest.mark.parametrize(
    "id_input",
    [
        "abc",
        "1.5",
        "1e3",
        "",
        "    ",
        None
    ],
    ids=[
        "non_numeric",
        "decimal",
        "scientific_notation",
        "empty_string",
        "whitespace_only",
        "none"
    ],
)
def test_validate_id_rejects_invalid_input(id_input):
    with pytest.raises(
        ValueError,
        match="ID必须为整数",
    ):
        validate_id(id_input)


@pytest.mark.parametrize(
    "id_input",
    [
        "0",
        "-12",
    ],
    ids=[
        "zero",
        "negative_integer",
    ],
)
def test_validate_id_rejects_out_of_range_integer(id_input):
    with pytest.raises(
        ValueError,
        match="ID必须大于0",
    ):
        validate_id(id_input)


@pytest.mark.parametrize(
    "category_input, expected_category",
    [
        ("food", "food"),
    ],
    ids=[
        "valid_string",
    ],
)
def test_validate_category_returns_valid_category_for_standard_input(category_input, expected_category):
    result = validate_category(category_input)
    assert result == expected_category


@pytest.mark.parametrize(
    "category_input, expected_category",
    [
        (" food ", "food"),
        ("  FOOD ", "FOOD"),
        ("  餐饮  ", "餐饮"),
    ],
    ids=[
        "string_surrounding_whitespace",
        "uppercase_with_whitespace",
        "chinese_with_whitespace",
    ],
)
def test_validate_category_normalizes_valid_category(category_input, expected_category):
    result = validate_category(category_input)

    assert result == expected_category


@pytest.mark.parametrize(
    "category_input",
    [
        "",
        "    ",
        None,
    ],
    ids=[
        "empty_string",
        "whitespace_only",
        "none",
    ],
)
def test_validate_category_rejects_invalid_input(category_input):
    with pytest.raises(
        ValueError,
        match="分类不能为空",
    ):
        validate_category(category_input)


@pytest.mark.parametrize(
    "start_date_input, end_date_input",
    [
        ("2026-08-01", "2026-08-31"),
        ("2026-08-23", "2026-08-23"),
        ("2026-12-31", "2027-01-01"),
    ],
    ids=[
        "same_month_forward",
        "same_date",
        "cross_year_forward",
    ],
)
def test_validate_date_range_accepts_valid_range(start_date_input, end_date_input):
    result = validate_date_range(start_date_input, end_date_input)
    assert result is None


def test_validate_date_range_rejects_reversed_range():
    with pytest.raises(
        ValueError,
        match="开始日期不能晚于结束日期",
    ):
        validate_date_range("2026-08-31", "2026-08-01")