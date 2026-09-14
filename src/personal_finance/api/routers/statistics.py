"""Statistics API routes."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends

from personal_finance.api.dependencies import get_statistics_service
from personal_finance.api.schemas import TransactionStatisticsResponse
from personal_finance.application.dto import StatisticsQuery
from personal_finance.application.services.statistics_service import (
    StatisticsService,
)


router = APIRouter(
    prefix="/statistics",
    tags=["statistics"],
)


@router.get(
    "",
    response_model=TransactionStatisticsResponse,
)
def get_statistics(
    service: Annotated[
        StatisticsService,
        Depends(get_statistics_service),
    ],
    start_date: date | None = None,
    end_date: date | None = None,
) -> TransactionStatisticsResponse:
    query = StatisticsQuery(
        start_date=start_date,
        end_date=end_date,
    )

    statistics = service.get(query)

    return TransactionStatisticsResponse.model_validate(statistics)
