from typing import Protocol

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


class TransactionRepository(Protocol):
    def add(self, data: CreateTransactionData) -> Transaction:
        ...

    def get(self, transaction_id: int) -> Transaction | None:
        ...

    def list(self, query: TransactionQuery) -> list[Transaction]:
        ...

    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction | None:
        ...

    def delete(self, transaction_id: int) -> bool:
        ...

    def summarize(self, query: StatisticsQuery) -> TransactionStatistics:
        ...
