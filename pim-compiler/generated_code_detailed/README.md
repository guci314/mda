# User Management System

This is a FastAPI-based user management system. It provides APIs for creating, reading, updating, and deleting users.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd generated_code_detailed
   ```

2. Install the dependencies:
   ```bash
   pip install -r user_management/requirements.txt
   ```

## Running the Application

1. Navigate to the project directory:
   ```bash
   cd user_management
   ```

2. Start the FastAPI server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```

   The `--reload` flag enables auto-reload for development.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Environment Variables

Create a `.env` file in the `user_management` directory with the following content:
```
DATABASE_URL=sqlite:///./user_management.db
SECRET_KEY=your-secret-key
```

## Database

The system uses SQLite by default. The database file will be created automatically at `user_management.db` when the application starts.

## Testing

To test the APIs, use tools like Postman or the interactive Swagger UI provided at `/docs`.