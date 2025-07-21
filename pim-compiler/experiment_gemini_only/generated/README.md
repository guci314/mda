# Blog System API

This project is a complete, production-ready Blog System API built with FastAPI, following the specifications of a Platform-Specific Model (PSM).

It includes user registration, authentication, and full CRUD operations for articles, comments, and tags.

## Features

- **Modern Tech Stack**: FastAPI, Pydantic v2, SQLAlchemy 2.0 (async).
- **Authentication**: JWT-based authentication with password hashing.
- **Database**: Asynchronous support for both SQLite (for easy setup) and PostgreSQL (for production).
- **Modular Design**: Code is organized into modules for `models`, `schemas`, `crud` (business logic), and `api` (endpoints).
- **Dependency Injection**: FastAPI's `Depends` system is used for managing database sessions and user authentication.
- **Database Migrations**: Basic Alembic setup for managing database schema changes.
- **Testing**: Includes a suite of unit tests using `pytest` and `httpx`.
- **Configuration**: Centralized settings management using `pydantic-settings`.

## Project Structure

```
.
├── app/                  # Main application package
│   ├── api/              # API routers and dependencies
│   ├── core/             # Configuration and security
│   ├── crud/             # Business logic (Create, Read, Update, Delete)
│   ├── db/               # Database session and models base
│   ├── models/           # SQLAlchemy ORM models
│   ├── schemas/          # Pydantic data validation models
│   └── main.py           # FastAPI app entrypoint
├── tests/                # Unit and integration tests
├── .env.example          # Example environment variables
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup and Installation

### 1. Prerequisites

- Python 3.10+
- A virtual environment tool (e.g., `venv`, `virtualenv`)

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and customize it if needed. For local development, the defaults (using SQLite) are sufficient.

```bash
cp .env.example .env
```
The `SECRET_KEY` should be changed for a production environment.

## Running the Application

### Development Server

The application uses `uvicorn` as the ASGI server.

```bash
uvicorn app.main:app --reload
```

The `--reload` flag makes the server restart after code changes.

The API will be available at `http://127.0.0.1:8000`.

### Interactive API Docs

FastAPI provides automatic interactive API documentation. Once the server is running, you can access them at:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Running Tests

The project is equipped with a test suite using `pytest`.

To run the tests:

```bash
pytest
```

The tests run against an in-memory SQLite database to ensure isolation from your development database.

## Database Migrations (Alembic)

This project is configured to use Alembic for database schema migrations, which is essential when you need to add or change models in a production environment.

**Note**: When the application starts, it automatically creates all tables from the models (`Base.metadata.create_all(engine)`). This is convenient for development but not suitable for production data management. For production, you should rely on Alembic.

### How to switch to PostgreSQL

1.  Install the required driver:
    ```bash
    pip install asyncpg
    ```
2.  Update the `DATABASE_URL` in your `.env` file:
    ```
    DATABASE_URL="postgresql+asyncpg://your_user:your_password@your_host:5432/your_db"
    ```
3.  Make sure your PostgreSQL server is running.

### Generating a new migration

When you change a SQLAlchemy model (e.g., add a new column), you can generate a migration script:

```bash
alembic revision --autogenerate -m "Describe your changes here"
```

### Applying a migration

To apply the latest migration to your database:

```bash
alembic upgrade head
```
