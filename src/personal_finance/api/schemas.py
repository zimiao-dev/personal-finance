"""Define API request and response schemas."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from personal_finance.domain.enums import TransactionType


class CreateTransactionRequest(BaseModel):
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None = None


class ReplaceTransactionRequest(BaseModel):
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None


class TransactionStatisticsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total_income: Decimal
    total_expense: Decimal
    transaction_count: int
    balance: Decimal
