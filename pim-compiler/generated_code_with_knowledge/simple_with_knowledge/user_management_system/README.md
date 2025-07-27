# User Management System

A simple FastAPI-based user management system with SQLite as the database.

## Features

- Create, read, update, and delete users
- RESTful API endpoints
- SQLAlchemy for database operations
- Pydantic for data validation

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd user_management_system
   ```

2. Install dependencies:
   ```bash
   pip install fastapi sqlalchemy pydantic uvicorn
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- `POST /api/v1/users/` - Create a new user
- `GET /api/v1/users/` - Get a list of users
- `GET /api/v1/users/{user_id}` - Get a single user
- `PUT /api/v1/users/{user_id}` - Update a user
- `DELETE /api/v1/users/{user_id}` - Delete a user

## Database

The application uses SQLite by default. The database file (`user_management.db`) will be created automatically when the application starts.

## Testing

To run tests, navigate to the `tests` directory and execute the test scripts.

## License

MIT