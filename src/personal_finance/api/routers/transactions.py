"""Transaction API routes."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from personal_finance.api.dependencies import get_transaction_service
from personal_finance.api.schemas import (
    CreateTransactionRequest,
    ReplaceTransactionRequest,
    TransactionResponse,
)
from personal_finance.application.dto import (
    CreateTransactionData,
    ReplaceTransactionData,
    TransactionQuery,
)
from personal_finance.application.services.transaction_service import (
    TransactionService,
)


router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    request: CreateTransactionRequest,
    service: Annotated[
        TransactionService,
        Depends(get_transaction_service),
    ],
) -> TransactionResponse:
    data = CreateTransactionData(
        amount=request.amount,
        type=request.type,
        category=request.category,
        transaction_date=request.transaction_date,
        description=request.description,
    )

    transaction = service.create(data)

    return TransactionResponse.model_validate(transaction)


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def list_transactions(
    service: Annotated[
        TransactionService,
        Depends(get_transaction_service),
    ],
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[TransactionResponse]:
    query = TransactionQuery(
        category=category,
        start_date=start_date,
        end_date=end_date,
    )

    transactions = service.list(query)

    return [
        TransactionResponse.model_validate(transaction)
        for transaction in transactions
    ]


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: int,
    service: Annotated[
        TransactionService,
        Depends(get_transaction_service),
    ],
) -> TransactionResponse:
    transaction = service.get(transaction_id)

    return TransactionResponse.model_validate(transaction)


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def replace_transaction(
    transaction_id: int,
    request: ReplaceTransactionRequest,
    service: Annotated[
        TransactionService,
        Depends(get_transaction_service),
    ],
) -> TransactionResponse:
    data = ReplaceTransactionData(
        amount=request.amount,
        type=request.type,
        category=request.category,
        transaction_date=request.transaction_date,
        description=request.description,
    )

    transaction = service.replace(
        transaction_id,
        data,
    )

    return TransactionResponse.model_validate(transaction)


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: int,
    service: Annotated[
        TransactionService,
        Depends(get_transaction_service),
    ],
) -> Response:
    service.delete(transaction_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
