# FastAPI User Management System

This is a FastAPI-based user management system that allows you to register, query, update, and delete users.

## Features

- User registration with email validation
- User listing with pagination
- User details retrieval
- User information update
- User deletion (soft delete by setting status to inactive)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd fastapi_user_management
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Documentation

After running the application, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

To run the tests, execute the following command:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License.