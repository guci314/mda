# User Management System

A FastAPI-based user management system with CRUD operations for users.

## Prerequisites

- Python 3.7+
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd user_management
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   uvicorn user_management.main:app --reload
   ```

## API Endpoints

- **GET /**: Root endpoint
- **POST /api/v1/users/**: Create a new user
- **GET /api/v1/users/**: List all users
- **GET /api/v1/users/{user_id}**: Get a specific user
- **PUT /api/v1/users/{user_id}**: Update a user
- **DELETE /api/v1/users/{user_id}**: Delete a user

## Database

The application uses SQLite by default. The database file (`user_management.db`) will be created automatically in the project directory.

## Environment Variables

- `DATABASE_URL`: Database connection URL (default: `sqlite:///./user_management.db`)
- `SECRET_KEY`: Secret key for security (default: `your-secret-key`)

Create a `.env` file in the project root to override these values.

## Testing

To test the API, you can use tools like Postman or curl. Example:

```bash
curl -X POST "http://localhost:8000/api/v1/users/" -H "Content-Type: application/json" -d '{"username":"testuser","email":"test@example.com","password":"password"}'
```

## License

MIT