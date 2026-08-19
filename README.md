# Personal Finance System

A command-line personal finance management system implemented with Python and SQLite.

This project provides basic personal finance management features, including transaction creation, modification, deletion, query, and financial statistics.

The project demonstrates Python backend development practices, including layered architecture, database operations, input validation, and service-oriented design.


## Features

- Add transaction
  - Record income and expense information
  - Store transaction amount, category, date and description

- List transactions
  - Display all transaction records

- Update transaction
  - Modify existing transaction information

- Delete transaction
  - Remove transaction records by ID

- Query transactions
  - Query by category
  - Query by date range
  - Query by category and date range

- Statistics
  - Calculate total income
  - Calculate total expense
  - Calculate balance


## Tech Stack

- Python
- SQLite
- Dataclass
- CLI Application


## Project Structure

```
personal-finance
│
├── main.py # CLI entry point
│
├── services.py # Business logic layer
│
├── models.py # Data models
│
├── validators.py # Input validation
│
├── database.py # Database connection
│
└── data
    └── finance.db
```

## Architecture

The project follows a simple layered architecture:

```
User Input
|
v
main.py
(CLI Layer)
|
v
validators.py
(Input Validation)
|
v
services.py
(Business Logic)
|
v
database.py
(Database Access)
|
v
SQLite
```

## Database Design

### transactions table

| Column | Type | Description |
|------|------|------|
| id | INTEGER | Primary key |
| amount | REAL | Transaction amount |
| type | TEXT | income / expense |
| category | TEXT | Transaction category |
| transaction_date | TEXT | Transaction date |
| description | TEXT | Additional notes |

