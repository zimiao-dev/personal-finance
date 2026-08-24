import pytest

import database


@pytest.fixture
def temporary_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "finance_test.db"

    monkeypatch.setattr(
        database,
        "DB_PATH",
        test_db_path,
    )

    database.create_table()

    return test_db_path