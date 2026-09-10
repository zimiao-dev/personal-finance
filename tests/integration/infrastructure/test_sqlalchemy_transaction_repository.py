from datetime import date
from decimal import Decimal

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    StatisticsQuery,
    TransactionQuery,
)
from personal_finance.domain.entities import (
    Transaction,
    TransactionStatistics,
)
from personal_finance.domain.enums import TransactionType
from personal_finance.infrastructure.database.base import Base
from personal_finance.infrastructure.database.models import TransactionModel
from personal_finance.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)


def test_sqlalchemy_transaction_repository_add_returns_domain_transaction_with_generated_id(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as session:
        # Act
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.add(create_data)

        # Assert
        assert isinstance(result, Transaction)
        assert not isinstance(result, TransactionModel)

        assert isinstance(result.id, int)
        assert result.id > 0

        assert result.amount == create_data.amount
        assert isinstance(result.amount, Decimal)

        assert result.type is create_data.type
        assert result.category == create_data.category
        assert result.transaction_date == create_data.transaction_date
        assert result.description == create_data.description


def test_sqlalchemy_transaction_repository_add_does_not_commit(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("18.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as write_session:
        # Act
        repository = SQLAlchemyTransactionRepository(write_session)

        result = repository.add(create_data)

        transaction_id = result.id

        with Session(engine) as read_session:
            stored_model = read_session.get(
                TransactionModel,
                transaction_id,
            )

            # Assert
            assert stored_model is None

        write_session.rollback()

    with Session(engine) as verification_session:
        assert verification_session.get(
            TransactionModel,
            transaction_id,
        ) is None


def test_sqlalchemy_transaction_repository_get_returns_domain_transaction(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    stored_model = TransactionModel(
        amount=Decimal("18.50"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 9),
        description="dinner",
    )

    with Session(engine) as write_session:
        write_session.add(stored_model)
        write_session.flush()

        transaction_id = stored_model.id

        write_session.commit()

    assert transaction_id is not None

    with Session(engine) as read_session:
        repository = SQLAlchemyTransactionRepository(read_session)
        result = repository.get(transaction_id)

    assert result is not None
    assert isinstance(result, Transaction)
    assert not isinstance(result, TransactionModel)

    assert result.id == transaction_id
    assert isinstance(result.amount, Decimal)
    assert result.amount == Decimal("18.50")
    assert result.type is TransactionType.EXPENSE
    assert result.category == "Food"
    assert result.transaction_date == date(2026, 9, 9)
    assert result.description == "dinner"


def test_sqlalchemy_transaction_repository_get_returns_none_when_missing(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    transaction_id = 999

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.get(transaction_id)

    # Assert
    assert result is None


def test_sqlalchemy_transaction_repository_replace_updates_all_business_fields(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    stored_model = TransactionModel(
        amount=Decimal("18.50"),
        type="income",
        category="transportation",
        transaction_date=date(2026, 9, 9),
        description="subway",
    )

    with Session(engine) as write_session:
        write_session.add(stored_model)
        write_session.flush()

        transaction_id = stored_model.id

        write_session.commit()

    assert transaction_id is not None

    replace_data = ReplaceTransactionData(
        amount=Decimal("20.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as session:
        # Act
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.replace(
            transaction_id,
            replace_data,
        )

        session.commit()

    with Session(engine) as verification_session:
        updated_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

    # Assert
    assert result is not None
    assert isinstance(result, Transaction)
    assert not isinstance(result, TransactionModel)

    assert result.id == transaction_id
    assert isinstance(result.amount, Decimal)
    assert result.amount == replace_data.amount
    assert result.type is TransactionType.EXPENSE
    assert result.category == replace_data.category
    assert result.transaction_date == replace_data.transaction_date
    assert result.description == replace_data.description

    assert updated_model is not None
    assert updated_model.amount == replace_data.amount
    assert updated_model.type == replace_data.type.value
    assert updated_model.category == replace_data.category
    assert updated_model.transaction_date == replace_data.transaction_date
    assert updated_model.description == replace_data.description


def test_sqlalchemy_transaction_repository_replace_returns_none_when_missing(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    transaction_id = 999

    replace_data = ReplaceTransactionData(
        amount=Decimal("20.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as session:
        # Act
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.replace(
            transaction_id,
            replace_data,
        )

    assert result is None


def test_sqlalchemy_transaction_repository_replace_same_values_still_returns_transaction(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    stored_model = TransactionModel(
        amount=Decimal("20.50"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as write_session:
        write_session.add(stored_model)
        write_session.flush()

        transaction_id = stored_model.id

        write_session.commit()

    assert transaction_id is not None

    replace_data = ReplaceTransactionData(
        amount=Decimal("20.50"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as session:
        # Act
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.replace(
            transaction_id,
            replace_data,
        )

        session.commit()

    with Session(engine) as verification_session:
        updated_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

    # Assert
    assert result is not None
    assert isinstance(result, Transaction)
    assert not isinstance(result, TransactionModel)

    assert result.id == transaction_id

    assert updated_model is not None


def test_sqlalchemy_transaction_repository_delete_returns_true_and_removes_existing_transaction(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    stored_model = TransactionModel(
        amount=Decimal("20.50"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    with Session(engine) as write_session:
        write_session.add(stored_model)
        write_session.flush()

        transaction_id = stored_model.id

        write_session.commit()

    assert transaction_id is not None

    with Session(engine) as session:
        # Act
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.delete(transaction_id)

        deleted_model = session.get(
            TransactionModel,
            transaction_id,
        )

        # Assert
        assert result is True
        assert deleted_model is None

        session.commit()

    with Session(engine) as verification_session:
        assert verification_session.get(
            TransactionModel,
            transaction_id,
        ) is None


def test_sqlalchemy_transaction_repository_delete_returns_false_when_missing(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    missing_transaction_id = 999

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.delete(missing_transaction_id)

    # Assert
    assert result is False


def test_sqlalchemy_transaction_repository_list_returns_empty_list_for_empty_table(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)
    query = TransactionQuery()

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.list(query)

    # Assert
    assert result == []
    assert isinstance(result, list)


def test_sqlalchemy_transaction_repository_list_returns_transactions_by_id_descending(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 5),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="transportation",
        transaction_date=date(2026, 9, 4),
        description="subway",
    )

    query = TransactionQuery()

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
            ]
        )

        write_session.flush()

        first_id = first_model.id
        second_id = second_model.id
        third_id = third_model.id

        write_session.commit()

    assert first_id is not None
    assert second_id is not None
    assert third_id is not None

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.list(query)

    # Assert
    assert all(
        isinstance(item, Transaction)
        for item in result
    )

    assert [item.id for item in result] == [
        third_id,
        second_id,
        first_id,
    ]


def test_sqlalchemy_transaction_repository_list_filters_by_exact_category(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 5),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="transportation",
        transaction_date=date(2026, 9, 4),
        description="subway",
    )

    query = TransactionQuery(category="Food")

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
            ]
        )

        write_session.flush()

        first_id = first_model.id
        second_id = second_model.id
        third_id = third_model.id

        write_session.commit()

    assert first_id is not None
    assert second_id is not None
    assert third_id is not None

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.list(query)

    # Assert
    assert all(
        isinstance(item, Transaction)
        for item in result
    )

    assert [item.id for item in result] == [
        second_id,
    ]


def test_sqlalchemy_transaction_repository_list_filters_by_inclusive_date_range(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 5),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("7.80"),
        type="expense",
        category="transportation",
        transaction_date=date(2026, 9, 4),
        description="subway",
    )

    fourth_model = TransactionModel(
        amount=Decimal("6.80"),
        type="expense",
        category="transportation",
        transaction_date=date(2026, 8, 31),
        description="subway",
    )

    query = TransactionQuery(
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 4),
    )

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
                fourth_model,
            ]
        )

        write_session.flush()

        first_id = first_model.id
        second_id = second_model.id
        third_id = third_model.id
        fourth_id = fourth_model.id

        write_session.commit()

    assert first_id is not None
    assert second_id is not None
    assert third_id is not None
    assert fourth_id is not None

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.list(query)

    # Assert
    assert all(
        isinstance(item, Transaction)
        for item in result
    )

    assert [item.id for item in result] == [
        third_id,
        first_id,
    ]


def test_sqlalchemy_transaction_repository_list_combines_filters_with_and(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 1),
        description="dinner",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 5),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 4),
        description="lunch",
    )

    query = TransactionQuery(
        category="Food",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 4),
    )

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
            ]
        )

        write_session.flush()

        first_id = first_model.id
        second_id = second_model.id
        third_id = third_model.id

        write_session.commit()

    assert first_id is not None
    assert second_id is not None
    assert third_id is not None

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.list(query)

    # Assert
    assert all(
        isinstance(item, Transaction)
        for item in result
    )

    assert [item.id for item in result] == [
        first_id,
    ]


def test_sqlalchemy_transaction_repository_summarize_returns_zero_statistics_for_empty_table(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    query = StatisticsQuery()

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.summarize(query)

    # Assert
    assert isinstance(result, TransactionStatistics)
    assert isinstance(result.total_income, Decimal)
    assert isinstance(result.total_expense, Decimal)

    assert result.total_income == Decimal("0")
    assert result.total_expense == Decimal("0")
    assert result.transaction_count == 0
    assert result.balance == Decimal("0")


def test_sqlalchemy_transaction_repository_summarize_aggregates_income_expense_and_count(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("10000.0001"),
        type="income",
        category="salary",
        transaction_date=date(2026, 8, 31),
        description="",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 2),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("99999999999.9999"),
        type="income",
        category="salary",
        transaction_date=date(2026, 9, 4),
        description="",
    )

    fourth_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 7),
        description="dinner",
    )

    expected_income = Decimal("10000.0001") + Decimal("99999999999.9999")
    expected_expense = Decimal("16.80") + Decimal("20.80")
    expected_count = 4

    query = StatisticsQuery()

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
                fourth_model,
            ]
        )

        write_session.commit()

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.summarize(query)

    # Assert
    assert isinstance(result, TransactionStatistics)
    assert isinstance(result.total_income, Decimal)
    assert isinstance(result.total_expense, Decimal)

    assert result.total_income == expected_income
    assert result.total_expense == expected_expense
    assert result.transaction_count == expected_count
    assert result.balance == expected_income - expected_expense


def test_sqlalchemy_transaction_repository_summarize_uses_inclusive_date_range(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    first_model = TransactionModel(
        amount=Decimal("10000.0001"),
        type="income",
        category="salary",
        transaction_date=date(2026, 8, 31),
        description="",
    )

    second_model = TransactionModel(
        amount=Decimal("16.80"),
        type="expense",
        category="Food",
        transaction_date=date(2026, 9, 2),
        description="lunch",
    )

    third_model = TransactionModel(
        amount=Decimal("99999999999.9999"),
        type="income",
        category="salary",
        transaction_date=date(2026, 9, 4),
        description="",
    )

    fourth_model = TransactionModel(
        amount=Decimal("20.80"),
        type="expense",
        category="food",
        transaction_date=date(2026, 9, 7),
        description="dinner",
    )

    expected_income = Decimal("99999999999.9999")
    expected_expense = Decimal("16.80")
    expected_count = 2

    query = StatisticsQuery(
        start_date=date(2026, 9, 2),
        end_date=date(2026, 9, 4),
    )

    with Session(engine) as write_session:
        write_session.add_all(
            [
                first_model,
                second_model,
                third_model,
                fourth_model,
            ]
        )

        write_session.commit()

    # Act
    with Session(engine) as session:
        repository = SQLAlchemyTransactionRepository(session)
        result = repository.summarize(query)

    # Assert
    assert isinstance(result, TransactionStatistics)
    assert isinstance(result.total_income, Decimal)
    assert isinstance(result.total_expense, Decimal)

    assert result.total_income == expected_income
    assert result.total_expense == expected_expense
    assert result.transaction_count == expected_count
    assert result.balance == expected_income - expected_expense
