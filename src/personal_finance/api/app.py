from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from personal_finance.api.routers.health import router as health_router
from personal_finance.api.routers.statistics import (
    router as statistics_router,
)
from personal_finance.api.routers.transactions import (
    router as transaction_router,
)
from personal_finance.application.exceptions import (
    TransactionNotFoundError,
)
from personal_finance.domain.exceptions import DomainValidationError


def create_app() -> FastAPI:
    app = FastAPI(
        title="Personal Finance API",
        version="0.2.0",
    )

    @app.exception_handler(TransactionNotFoundError)
    def handle_transaction_not_found(
        _request: Request,
        exc: TransactionNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(DomainValidationError)
    def handle_domain_validation_error(
        _request: Request,
        exc: DomainValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": str(exc)},
        )

    app.include_router(health_router)
    app.include_router(transaction_router)
    app.include_router(statistics_router)

    return app
