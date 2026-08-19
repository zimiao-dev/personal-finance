import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

DB_DIR = BASE_DIR / "data"

DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "finance.db"


def get_connection() -> sqlite3.Connection:
    """
    获取数据库连接
    """
    return sqlite3.connect(DB_PATH)


def create_table():
    """
    创建 transactions 表
    """

    sql = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL CHECK(amount > 0),
        type TEXT NOT NULL CHECK(type IN ('income','expense')),
        category TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """

    with get_connection() as conn:
        conn.execute(sql)


if __name__ == "__main__":
    create_table()
    print("Database initialized successfully.")