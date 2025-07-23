# Project README

This is a FastAPI application for a Library Borrowing System, generated based on a Platform Specific Model (PSM).

## Setup

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**
    Copy `.env.example` to `.env` and fill in the details, especially the `DATABASE_URL`.
    ```bash
    cp .env.example .env
    ```
    Example `DATABASE_URL` for PostgreSQL:
    `DATABASE_URL=postgresql://user:password@host:port/dbname`

4.  **Run database migrations:**
    ```bash
    alembic upgrade head
    ```

## Running the Application

To run the development server:
```bash
python main.py
```
Or using uvicorn directly:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the test suite:
```bash
pytest
```
