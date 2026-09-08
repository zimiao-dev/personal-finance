from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import Date, DateTime, inspect, Integer, Numeric, Text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from personal_finance.infrastructure.database.base import Base
from personal_finance.infrastructure.database.models import TransactionModel


def test_sqlalchemy_metadata_creates_transactions_table(
    engine: Engine,
) -> None:
    # Arrange + Act
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # Assert
    assert "transactions" in table_names


def test_sqlalchemy_transactions_table_has_expected_columns_and_types(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    inspector = inspect(engine)

    # Act
    columns = inspector.get_columns("transactions")

    column_names = [column["name"] for column in columns]

    # Assert
    assert column_names == [
        "id",
        "amount",
        "type",
        "category",
        "transaction_date",
        "description",
        "created_at",
    ]

    id_column = next(
        column for column in columns
        if column["name"] == "id"
    )

    assert isinstance(id_column["type"], Integer)

    amount_column = next(
        column for column in columns
        if column["name"] == "amount"
    )

    assert isinstance(amount_column["type"], Numeric)
    assert amount_column["type"].precision == 15
    assert amount_column["type"].scale == 4

    type_column = next(
        column for column in columns
        if column["name"] == "type"
    )

    assert isinstance(type_column["type"], Text)

    category_column = next(
        column for column in columns
        if column["name"] == "category"
    )

    assert isinstance(category_column["type"], Text)

    transaction_date_column = next(
        column for column in columns
        if column["name"] == "transaction_date"
    )

    assert isinstance(transaction_date_column["type"], Date)

    description_column = next(
        column for column in columns
        if column["name"] == "description"
    )

    assert isinstance(description_column["type"], Text)

    created_at_column = next(
        column for column in columns
        if column["name"] == "created_at"
    )

    assert isinstance(created_at_column["type"], DateTime)


def test_sqlalchemy_transactions_table_declares_expected_constraints(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    inspector = inspect(engine)

    # Act
    columns = inspector.get_columns("transactions")
    primary_key = inspector.get_pk_constraint("transactions")
    check_constraints = inspector.get_check_constraints("transactions")

    columns_by_name = {
        column["name"]: column
        for column in columns
    }

    constraint_names = {
        constraint["name"]
        for constraint in check_constraints
    }

    # Assert
    assert primary_key["constrained_columns"] == ["id"]

    assert columns_by_name["id"]["nullable"] is False
    assert columns_by_name["amount"]["nullable"] is False
    assert columns_by_name["type"]["nullable"] is False
    assert columns_by_name["category"]["nullable"] is False
    assert columns_by_name["transaction_date"]["nullable"] is False
    assert columns_by_name["description"]["nullable"] is True
    assert columns_by_name["created_at"]["nullable"] is False

    created_at_default = columns_by_name["created_at"]["default"]
    assert created_at_default is not None
    assert "CURRENT_TIMESTAMP" in created_at_default.upper()

    assert "ck_transactions_amount_positive" in constraint_names
    assert "ck_transactions_type_valid" in constraint_names


@pytest.mark.parametrize(
    "amount_value",
    [
        Decimal("0"),
        Decimal("-0.0001"),
    ],
    ids=[
        "zero",
        "negative",
    ],
)
def test_sqlalchemy_transactions_table_rejects_non_positive_amount(
    engine: Engine,
    amount_value: Decimal,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    transaction_model = TransactionModel(
        amount=amount_value,
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    # Act + Assert
    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            session.add(transaction_model)
            session.flush()


def test_sqlalchemy_transactions_table_rejects_invalid_transaction_type(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    transaction_model = TransactionModel(
        amount=Decimal("10.80"),
        type="transfer",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    # Act + Assert
    with Session(engine) as session:
        with pytest.raises(IntegrityError):
            session.add(transaction_model)
            session.flush()


@pytest.mark.parametrize(
    "amount_value",
    [
        Decimal("0.0001"),
        Decimal("0.1"),
        Decimal("1"),
        Decimal("128.50"),
        Decimal("99999999999.9999"),
    ],
    ids=[
        "minimum_supported",
        "single_decimal_place",
        "integer_value",
        "two_decimal_places",
        "maximum_supported",
    ],
)
def test_sqlalchemy_numeric_round_trip_preserves_supported_amount(
    engine: Engine,
    amount_value: Decimal,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    transaction_model = TransactionModel(
        amount=amount_value,
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    # Act
    with Session(engine) as write_session:
        write_session.add(transaction_model)
        write_session.flush()

        transaction_id = transaction_model.id

        write_session.commit()

    # Assert
    assert transaction_id is not None

    # Act
    with Session(engine) as read_session:
        stored_transaction = read_session.get(
            TransactionModel,
            transaction_id,
        )

    # Assert
    assert stored_transaction is not None
    assert isinstance(stored_transaction.amount, Decimal)
    assert stored_transaction.amount == amount_value
