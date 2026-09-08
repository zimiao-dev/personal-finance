from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def create_engine_from_url(database_url: str) -> Engine:
    return create_engine(
        url=database_url,
        connect_args={"check_same_thread": False},
    )
