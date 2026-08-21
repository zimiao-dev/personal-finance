# Personal Finance System

A command-line personal finance management system implemented with Python and SQLite.

The project provides transaction creation, modification, deletion, filtering, and financial statistics. It demonstrates layered Python application design, SQLite data access, input validation, and service-oriented organization.

## Features

- Add income and expense transactions
- List all transactions
- Update and delete transactions by ID
- Query by category, date range, or both
- Calculate total income, total expense, and balance
- Validate amount, type, category, ID, and strict `YYYY-MM-DD` dates

## Tech Stack

- Python 3.10+
- SQLite
- Dataclasses
- CLI application

## Project Structure

```text
personal-finance/
├── main.py
├── database.py
├── models.py
├── validators.py
├── repositories/
│   ├── __init__.py
│   ├── transaction_repository.py
│   └── statistics_repository.py
├── services/
│   ├── __init__.py
│   ├── transaction_service.py
│   └── statistics_service.py
├── docs/
│   ├── requirements.md
│   └── database-design.md
└── data/
    └── finance.db
```

## Architecture

```text
User
  ↓
main.py                 CLI and output
  ↓
validators.py           Input validation
  ↓
services/               Application services
  ↓
repositories/           SQL and row mapping
  ↓
database.py             SQLite connection
  ↓
SQLite
```

## Database Design

### transactions

| Column | Type | Constraint | Description |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY | Transaction ID |
| amount | REAL | NOT NULL, > 0 | Transaction amount |
| type | TEXT | income / expense | Transaction type |
| category | TEXT | NOT NULL | Transaction category |
| transaction_date | TEXT | NOT NULL | Date in YYYY-MM-DD format |
| description | TEXT | NULL | Optional note |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP | Creation time |

Input dates are validated by the application. SQLite stores them as text.

## Run

Initialize the database:

```bash
python database.py
```

Start the CLI:

```bash
python main.py
```
