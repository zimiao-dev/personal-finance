from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    TransactionQuery,
)
from personal_finance.application.exceptions import TransactionNotFoundError
from personal_finance.application.ports.unit_of_work import UnitOfWork
from personal_finance.domain.entities import Transaction
from personal_finance.domain.rules import (
    validate_transaction_id,
)


class TransactionService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def create(self, data: CreateTransactionData) -> Transaction:
        with self._uow as uow:
            transaction = uow.transactions.add(data)
            uow.commit()

        return transaction

    def get(self, transaction_id: int) -> Transaction:
        transaction_id = validate_transaction_id(transaction_id)

        with self._uow as uow:
            transaction = uow.transactions.get(transaction_id)

            if transaction is None:
                raise TransactionNotFoundError(
                    f"transaction {transaction_id} was not found",
                )

            return transaction

    def list(self, query: TransactionQuery) -> list[Transaction]:
        with self._uow as uow:
            transactions = uow.transactions.list(query)

        return transactions

    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction:
        transaction_id = validate_transaction_id(transaction_id)

        with self._uow as uow:
            transaction = uow.transactions.replace(transaction_id, data)

            if transaction is None:
                raise TransactionNotFoundError(
                    f"transaction {transaction_id} was not found",
                )

            uow.commit()

        return transaction

    def delete(self, transaction_id: int) -> None:
        transaction_id = validate_transaction_id(transaction_id)

        with self._uow as uow:
            result = uow.transactions.delete(transaction_id)

            if result is False:
                raise TransactionNotFoundError(
                    f"transaction {transaction_id} was not found",
                )

            uow.commit()

        return None
