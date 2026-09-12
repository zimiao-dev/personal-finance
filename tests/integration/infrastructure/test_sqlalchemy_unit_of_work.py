from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from personal_finance.application.dto import CreateTransactionData
from personal_finance.domain.enums import TransactionType
from personal_finance.infrastructure.database.base import Base
from personal_finance.infrastructure.database.engine import create_session_factory
from personal_finance.infrastructure.database.unit_of_work import (
    SQLAlchemyUnitOfWork,
)
from personal_finance.infrastructure.database.models import TransactionModel


def test_sqlalchemy_unit_of_work_commit_persists_changes(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
    )

    session_factory = create_session_factory(engine)

    uow = SQLAlchemyUnitOfWork(session_factory)

    # Act
    with uow as entered_uow:
        result = entered_uow.transactions.add(create_data)
        transaction_id = result.id
        entered_uow.commit()

    # Assert
    assert isinstance(transaction_id, int)

    with Session(engine) as verification_session:
        stored_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

        assert stored_model is not None
        assert stored_model.amount == create_data.amount
        assert stored_model.type == create_data.type.value
        assert stored_model.transaction_date == create_data.transaction_date
        assert stored_model.description == create_data.description


def test_sqlalchemy_unit_of_work_rolls_back_when_exception_escapes(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
    )

    class ExceptionUoWError(Exception):
        pass

    session_factory = create_session_factory(engine)

    # Act + Assert
    with pytest.raises(
        ExceptionUoWError,
        match="expected uow rollback sentinel",
    ):
        with SQLAlchemyUnitOfWork(session_factory) as uow:
            result = uow.transactions.add(create_data)
            transaction_id = result.id
            raise ExceptionUoWError(
                "expected uow rollback sentinel",
            )

    with session_factory() as verification_session:
        stored_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

        assert stored_model is None


def test_sqlalchemy_unit_of_work_rolls_back_uncommitted_normal_exit(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
    )

    session_factory = create_session_factory(engine)

    with SQLAlchemyUnitOfWork(session_factory) as uow:
        result = uow.transactions.add(create_data)
        transaction_id = result.id

    with Session(engine) as verification_session:
        stored_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

        assert stored_model is None


def test_sqlalchemy_unit_of_work_explicit_rollback_discards_changes(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
    )

    session_factory = create_session_factory(engine)

    # Act
    with SQLAlchemyUnitOfWork(session_factory) as uow:
        result = uow.transactions.add(create_data)
        transaction_id = result.id
        uow.rollback()

    # Assert
    with Session(engine) as verification_session:
        stored_model = verification_session.get(
            TransactionModel,
            transaction_id,
        )

        assert stored_model is None


def test_sqlalchemy_unit_of_work_closes_session_after_exit(
    engine: Engine,
) -> None:
    # Arrange
    Base.metadata.create_all(engine)

    create_data = CreateTransactionData(
        amount=Decimal("10.80"),
        type=TransactionType.EXPENSE,
        category="Food",
        transaction_date=date(2026, 9, 1),
    )

    class RecordingSession(Session):
        def __init__(self, *args, **kwargs) -> None:
            super().__init__(*args, **kwargs)
            self.close_call_count = 0

        def close(self) -> None:
            self.close_call_count += 1
            super().close()

    created_sessions: list[RecordingSession] = []

    def recording_session_factory() -> RecordingSession:
        session = RecordingSession(bind=engine)
        created_sessions.append(session)
        return session

    # Act
    with SQLAlchemyUnitOfWork(recording_session_factory) as uow:
        uow.transactions.add(create_data)
        uow.commit()

    # Assert
    assert len(created_sessions) == 1
    assert created_sessions[0].close_call_count == 1
