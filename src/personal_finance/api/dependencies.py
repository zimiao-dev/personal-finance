"""Define API dependency providers and cross-layer composition."""

from personal_finance.application.services.statistics_service import (
    StatisticsService,
)
from personal_finance.application.services.transaction_service import (
    TransactionService,
)
from personal_finance.config import Settings
from personal_finance.infrastructure.database.engine import (
    create_engine_from_url,
    create_session_factory,
)
from personal_finance.infrastructure.database.unit_of_work import (
    SQLAlchemyUnitOfWork,
)


settings = Settings()
engine = create_engine_from_url(settings.database_url)
session_factory = create_session_factory(engine)


def get_transaction_service() -> TransactionService:
    uow = SQLAlchemyUnitOfWork(session_factory)

    return TransactionService(uow)


def get_statistics_service() -> StatisticsService:
    uow = SQLAlchemyUnitOfWork(session_factory)

    return StatisticsService(uow)
