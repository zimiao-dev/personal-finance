from sqlalchemy.orm import Session

from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
)
from personal_finance.domain.entities import Transaction
from personal_finance.infrastructure.database.models import TransactionModel
from personal_finance.infrastructure.database.mappers import (
    apply_replace_data_to_transaction_model,
    create_data_to_transaction_model,
    transaction_model_to_domain,
)


class SQLAlchemyTransactionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        data: CreateTransactionData,
    ) -> Transaction:
        model = create_data_to_transaction_model(data)

        self._session.add(model)
        self._session.flush()

        return transaction_model_to_domain(model)

    def get(
        self,
        transaction_id: int,
    ) -> Transaction | None:
        model = self._session.get(
            TransactionModel,
            transaction_id,
        )

        if model is None:
            return None

        return transaction_model_to_domain(model)

    def replace(
        self,
        transaction_id: int,
        data: ReplaceTransactionData,
    ) -> Transaction | None:
        model = self._session.get(
            TransactionModel,
            transaction_id,
        )

        if model is None:
            return None

        apply_replace_data_to_transaction_model(model, data)
        self._session.flush()

        return transaction_model_to_domain(model)

    def delete(
        self,
        transaction_id: int,
    ) -> bool:
        model = self._session.get(
            TransactionModel,
            transaction_id,
        )

        if model is None:
            return False

        self._session.delete(model)
        self._session.flush()

        return True
