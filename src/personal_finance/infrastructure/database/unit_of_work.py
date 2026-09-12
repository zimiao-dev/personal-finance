from collections.abc import Callable
from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from personal_finance.infrastructure.repositories.sqlalchemy_transaction_repository import (
    SQLAlchemyTransactionRepository,
)


class SQLAlchemyUnitOfWork:
    def __init__(
        self,
        session_factory: Callable[[], Session],
    ) -> None:
        self._session_factory = session_factory
        self._session: Session | None = None
        self._transactions: SQLAlchemyTransactionRepository | None = None

    @property
    def transactions(self) -> SQLAlchemyTransactionRepository:
        if self._transactions is None:
            raise RuntimeError("Unit of work is not active")

        return self._transactions

    def __enter__(self) -> Self:
        if self._session is not None:
            raise RuntimeError("Unit of work is already active")

        self._session = self._session_factory()
        self._transactions = SQLAlchemyTransactionRepository(self._session)

        return self

    def _require_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Unit of work is not active")

        return self._session

    def commit(self) -> None:
        session = self._require_session()
        session.commit()

    def rollback(self) -> None:
        session = self._require_session()
        session.rollback()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        session = self._session

        if session is None:
            return

        try:
            if session.in_transaction():
                session.rollback()
        finally:
            session.close()
            self._session = None
            self._transactions = None
