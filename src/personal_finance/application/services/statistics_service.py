from personal_finance.application.dto import StatisticsQuery
from personal_finance.application.ports.unit_of_work import UnitOfWork
from personal_finance.domain.entities import TransactionStatistics


class StatisticsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def get(self, query: StatisticsQuery) -> TransactionStatistics:
        with self._uow as uow:
            transaction_statistics = uow.transactions.summarize(query)

        return transaction_statistics
