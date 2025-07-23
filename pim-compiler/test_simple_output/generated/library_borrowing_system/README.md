# Library Borrowing System

This is a FastAPI-based microservice for a Library Borrowing System, generated based on a Platform-Specific Model (PSM).

## Features

-   **Book Management**: Add, update, and query books.
-   **Reader Management**: Register, update, and manage readers.
-   **Borrowing Service**: Borrow, return, renew, and reserve books.
-   **Modern Tech Stack**: FastAPI, Pydantic v2, SQLAlchemy 2.0.
-   **Database Migrations**: Alembic for schema management.
-   **Dependency Management**: Pre-configured `requirements.txt`.
-   **Testing**: Unit and API tests with `pytest`.

## Setup and Installation

### Prerequisites

-   Python 3.10+
-   PostgreSQL (recommended for production) or SQLite

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd library_borrowing_system
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    -   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    -   Modify the `.env` file with your database URL and a secure secret key. For local development, the default SQLite setting is sufficient.

5.  **Run database migrations:**
    -   This command creates the database tables based on the SQLAlchemy models.
    ```bash
    alembic upgrade head
    ```

## Running the Application

To start the development server, run the main application file:

```bash
python main.py
```

The server will start, and you can access the interactive API documentation at:

-   **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
-   **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

To include coverage reports:

```bash
pytest --cov=app
```

## Project Structure

The project follows a modular structure:

-   `main.py`: Application entry point.
-   `app/`: Main application package.
    -   `main.py`: FastAPI app instance and configuration.
    -   `api/`: API routers and endpoints.
    -   `core/`: Configuration and core settings.
    -   `db/`: Database session management.
    -   `models/`: SQLAlchemy data models.
    -   `schemas/`: Pydantic data schemas.
    -   `crud/`: Reusable CRUD logic.
    -   `services/`: Business logic implementation.
-   `tests/`: Unit and API tests.
-   `alembic/`: Database migration scripts.
-   `requirements.txt`: Project dependencies.
-   `.env`: Environment variables file.

---
*This project was auto-generated.*
