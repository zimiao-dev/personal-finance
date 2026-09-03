from typing import Literal, TypedDict

from fastapi import APIRouter, status


router = APIRouter()


class HealthResponse(TypedDict):
    status: Literal["ok"]


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> HealthResponse:
    return {"status": "ok"}
