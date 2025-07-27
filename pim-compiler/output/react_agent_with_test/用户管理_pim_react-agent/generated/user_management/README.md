# User Management System

A FastAPI-based user management system with PostgreSQL database support.

## Features

- User registration
- User listing with pagination
- User details retrieval
- User information update
- User deletion (soft delete)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/user_management.git
   cd user_management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:
   - Ensure PostgreSQL is running.
   - Update the `DATABASE_URL` in `config/config.py`.

4. Run the application:
   ```bash
   uvicorn user_management.main:app --reload
   ```

## Testing

Run the tests with pytest:
```bash
pytest user_management/tests/
```

## API Documentation

After running the application, access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`