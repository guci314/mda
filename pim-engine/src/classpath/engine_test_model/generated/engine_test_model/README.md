# Engine Test Model (FastAPI)

## Description

This project implements a RESTful API using FastAPI, SQLAlchemy, and Pydantic. It provides endpoints for managing products and orders.

## Tech Stack

-   FastAPI
-   SQLAlchemy 2.0
-   Pydantic v2
-   PostgreSQL or SQLite
-   pytest
-   Poetry (for dependency management)

## Setup

1.  Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2.  Configure the database:

    -   Set the database URL in the `.env` file.

3.  Run the application:

    ```bash
    uvicorn app.main:app --reload
    ```

## Testing

```bash
pytest tests/test_api.py
```