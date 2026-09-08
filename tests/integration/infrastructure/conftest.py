from collections.abc import Generator

import pytest
from sqlalchemy.engine import Engine

from personal_finance.infrastructure.database.engine import (
    create_engine_from_url,
)


@pytest.fixture
def engine(tmp_path) -> Generator[Engine, None, None]:
    database_path = tmp_path / "finance_v2_test.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    engine = create_engine_from_url(database_url)

    yield engine

    engine.dispose()
