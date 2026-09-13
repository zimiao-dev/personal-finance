from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
)

from personal_finance.domain.entities import Transaction
from personal_finance.domain.enums import TransactionType

from .models import TransactionModel


def transaction_model_to_domain(
    model: TransactionModel,
) -> Transaction:
    return Transaction(
        id=model.id,
        amount=model.amount,
        type=TransactionType(model.type),
        category=model.category,
        transaction_date=model.transaction_date,
        description=model.description,
    )


def create_data_to_transaction_model(
    data: CreateTransactionData,
) -> TransactionModel:
    return TransactionModel(
        amount=data.amount,
        type=data.type.value,
        category=data.category,
        transaction_date=data.transaction_date,
        description=data.description,
    )


def apply_replace_data_to_transaction_model(
    model: TransactionModel,
    data: ReplaceTransactionData,
) -> None:
    model.amount = data.amount
    model.type = data.type.value
    model.category = data.category
    model.transaction_date = data.transaction_date
    model.description = data.description
