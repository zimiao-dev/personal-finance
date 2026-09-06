from types import TracebackType
from typing import Self

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    StatisticsQuery,
    TransactionQuery,
)
from personal_finance.application.ports.repositories import (
    TransactionRepository,
)
from personal_finance.domain.entities import (
    Transaction,
    TransactionStatistics,
)


class FakeUnitOfWork:
    def __init__(
        self,
        transactions: TransactionRepository,
        events: list[str],
    ) -> None:
        self.transactions = transactions

        self.enter_count = 0
        self.exit_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.exit_exception_type: type[BaseException] | None = None

        self.events: list[str] = events

    def __enter__(self) -> Self:
        self.enter_count += 1
        self.events.append("enter")
        return self

    def commit(self) -> None:
        self.commit_count += 1
        self.events.append("commit")

    def rollback(self) -> None:
        self.rollback_count += 1
        self.events.append("rollback")

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.exit_exception_type = exc_type

        if exc_type is not None:
            self.rollback()

        self.exit_count += 1
        self.events.append("exit")
        return None


class FakeTransactionRepository:
    def __init__(
        self,
        events: list[str],
    ) -> None:
        self.events: list[str] = events

        self.add_result: Transaction
        self.get_result: Transaction | None = None
        self.replace_result: Transaction | None = None
        self.list_result: list[Transaction] = []
        self.delete_result: bool
        self.summarize_result: TransactionStatistics

        self.added_data: list[CreateTransactionData] = []
        self.gotten_ids: list[int] = []
        self.listed_queries: list[TransactionQuery] = []
        self.replaced_arguments: list[tuple[int, ReplaceTransactionData]] = []
        self.deleted_ids: list[int] = []
        self.summarized_queries: list[StatisticsQuery] = []

    def add(self, data: CreateTransactionData) -> Transaction:
        self.added_data.append(data)
        self.events.append("add")
        return self.add_result

    def get(self, transaction_id: int) -> Transaction | None:
        self.gotten_ids.append(transaction_id)
        self.events.append("get")
        return self.get_result

    def list(self, query: TransactionQuery) -> list[Transaction]:
        self.listed_queries.append(query)
        self.events.append("list")
        return self.list_result

    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction | None:
        self.replaced_arguments.append((transaction_id, data))
        self.events.append("replace")
        return self.replace_result

    def delete(self, transaction_id: int) -> bool:
        self.deleted_ids.append(transaction_id)
        self.events.append("delete")
        return self.delete_result

    def summarize(self, query: StatisticsQuery) -> TransactionStatistics:
        self.summarized_queries.append(query)
        self.events.append("summarize")
        return self.summarize_result
