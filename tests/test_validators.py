import pytest

from validators import(
    validate_amount,
    validate_date
)


@pytest.mark.parametrize(
        'raw_amount, expected',
        [
            ("100", 100.0),
            ("100.5", 100.5),
            ("  88.6  ", 88.6)
        ],
        ids=[
            "integer",
            "decimal",
            "with_whitespace"
        ],
)
def test_validate_amount_with_valid_value(raw_amount, expected):
    result = validate_amount(raw_amount)

    assert result == expected


def test_validate_amount_with_zero():
    with pytest.raises(ValueError, match="金额必须大于0"):
        validate_amount("0")


@pytest.mark.parametrize(
    "invalid_amount",
    ["-1", "-100.5", "abc", "", "   ", None],
    ids=[
        "negative_integer",
        "negative_decimal",
        "non_numeric",
        "empty_string",
        "whitespace",
        "none",
    ],
)
def test_validate_amount_with_invalid_value(invalid_amount):
    with pytest.raises(ValueError):
        validate_amount(invalid_amount)


@pytest.mark.parametrize(
    'non_finite_amount',
    ['nan', 'inf', '-inf'],
    ids=[
        'not_a_number',
        'infinity',
        'negative_infinity'
    ],
)
def test_validate_amount_with_non_finite_value(non_finite_amount):
    with pytest.raises(ValueError, match="金额必须是有限数字"):
        validate_amount(non_finite_amount)


@pytest.mark.parametrize(
    "raw_date, expected",
    [
        ("2026-08-21", "2026-08-21"),
        ("  2026-08-21  ", "2026-08-21"),
        ("2024-02-29", "2024-02-29")
    ],
    ids=[
        "normal_date",
        "with_whitespace",
        "leap_year_date"
    ],

)
def test_validate_date_with_valid_value(raw_date, expected):
    result = validate_date(raw_date)

    assert result == expected


@pytest.mark.parametrize(
    'invalid_date',
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
        "month_not_padded",
        "day_not_padded",
        "wrong_separator",
        "wrong_order",
        "invalid_month",
        "invalid_day",
        "empty_string",
        "whitespace",
        "none",
    ]
)
def test_validate_date_with_invalid_value(invalid_date):
    with pytest.raises(
        ValueError,
        match="日期格式错误，应为 YYYY-MM-DD",
    ):
        validate_date(invalid_date)


