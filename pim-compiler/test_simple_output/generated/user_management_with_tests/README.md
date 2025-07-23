# User Management API

This project is a FastAPI-based user management system generated from a Platform-Specific Model (PSM). It includes user registration, authentication, and a full suite of tests.

## 1. Project Setup

### Prerequisites
- Python 3.10+
- Pip

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd user_management_with_tests
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

4.  **Set up environment variables:**
    Create a `.env` file by copying the example file:
    ```bash
    cp .env.example .env
    ```
    You can modify the variables in `.env` as needed. The `SECRET_KEY` should be replaced with a new secure key for production.

## 2. Running the Application

### Database Migrations (with Alembic)
This project is set up with Alembic for database migrations, but the initial migration files are not yet created. To create them:
```bash
# This will create the initial database schema based on the models
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Start the Server
Use Uvicorn to run the FastAPI application:
```bash
uvicorn app.main:app --reload
```
The application will be available at `http://127.0.0.1:8000`.

### API Documentation
Once the server is running, interactive API documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## 3. Running Tests

This project uses `pytest`. To run the test suite:

```bash
pytest
```

To get a coverage report:
```bash
pytest --cov=app
```

This will run all tests located in the `tests/` directory. The tests use an in-memory SQLite database, so they do not affect your development database.
