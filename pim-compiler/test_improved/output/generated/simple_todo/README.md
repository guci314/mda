# Simple Todo API

This project is a RESTful API for managing a simple Todo list, generated based on a Platform-Specific Model (PSM) document. It is built with Python using the FastAPI framework and follows modern development best practices.

## Features

- **Create, Read, Update, Delete (CRUD)** operations for Todo items.
- **FastAPI**: High-performance web framework.
- **SQLAlchemy 2.0**: Asynchronous ORM for database interaction.
- **Pydantic V2**: Robust data validation and settings management.
- **Dependency Injection**: Decoupled and testable components.
- **Automated Testing**: Unit tests with Pytest.
- **Auto-generated Documentation**: Interactive API documentation with Swagger UI and ReDoc.

## Project Structure

```
.
├── requirements.txt        # Project dependencies
├── src/                    # Main source code
│   ├── api/                # API endpoint routers
│   ├── core/               # Core components (config, db)
│   ├── models/             # SQLAlchemy ORM models
│   ├── schemas/            # Pydantic data schemas
│   ├── services/           # Business logic layer
│   └── main.py             # FastAPI application entrypoint
└── tests/                  # Unit and integration tests
```

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` and `venv`

### 1. Clone the Repository

```bash
# This step is illustrative. You are already in the project directory.
# git clone <repository_url>
# cd simple_todo
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
python -m venv venv
source venv/bin/activate
# On Windows, use: venv\Scripts\activate
```

### 3. Install Dependencies

Install all required packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

## Running the Application

The application is served using Uvicorn, an ASGI server.

```bash
uvicorn src.main:app --reload
```

- `--reload`: Enables auto-reload, so the server will restart after code changes.

The API will be available at `http://127.0.0.1:8000`.

## API Documentation

Once the application is running, you can access the interactive API documentation in your browser:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Running Tests

The project uses `pytest` for testing. To run the test suite, execute the following command from the project root directory:

```bash
pytest
```

The tests run against an in-memory SQLite database, so they do not affect your development database.

## Database Migrations (Production)

The application is configured to use a local SQLite database (`simple_todo.db`) by default, and it creates the necessary tables on startup.

For a production environment, you should use a more robust database (like PostgreSQL) and manage database schema changes with a migration tool like **Alembic** (which is already included in `requirements.txt`).

You would typically initialize Alembic and then create and apply migrations whenever you change your SQLAlchemy models.
