from types import TracebackType
from typing import Protocol, Self

from personal_finance.application.ports.repositories import TransactionRepository


class UnitOfWork(Protocol):
    transactions: TransactionRepository

    def __enter__(self) -> Self:
        ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
