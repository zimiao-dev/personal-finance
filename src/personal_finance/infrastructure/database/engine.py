from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker


def create_engine_from_url(database_url: str) -> Engine:
    url = make_url(database_url)

    if (
        url.get_backend_name() == "sqlite"
        and url.database is not None
        and url.database != ":memory:"
    ):
        Path(url.database).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    return create_engine(
        url=database_url,
        connect_args={"check_same_thread": False},
    )


def create_session_factory(
    engine: Engine,
) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )
