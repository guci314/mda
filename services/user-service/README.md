# User Service - 用户管理服务

Generated from PSM model using MDA approach.

## Features

- Complete CRUD operations for user management
- RESTful API with FastAPI
- PostgreSQL database with SQLAlchemy ORM
- Pydantic for data validation
- Built-in flow debugger at `/debug` endpoint
- Docker support

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Copy environment variables
cp .env.example .env

# Start services
docker-compose up -d

# Access the service
# API Documentation: http://localhost:8000/docs
# Flow Debugger: http://localhost:8000/debug/ui
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Run the service:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /api/v1/users` - Create a new user
- `GET /api/v1/users` - List users (paginated)
- `GET /api/v1/users/{user_id}` - Get user details
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Soft delete user

## Debug Interface

The service includes a flow debugger accessible at:
- Debug API: `http://localhost:8000/debug`
- Debug UI: `http://localhost:8000/debug/ui`

Features:
- Visual flow diagrams
- Breakpoint management
- Step-by-step execution
- Context inspection
- Execution history

## Testing with Debug Mode

To test the create user flow with debugging:

```bash
# Send request with debug header
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -H "X-Debug-Mode: debug" \
  -d '{
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "+8613812345678"
  }'
```

Then open `http://localhost:8000/debug/ui` to visualize the execution flow.

## Project Structure

```
user-service/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core configuration
│   ├── debug/        # Debug module
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── main.py       # Application entry
├── tests/            # Test files
├── requirements.txt  # Python dependencies
├── Dockerfile       # Docker image
└── docker-compose.yml
```

## MDA Markers

This code is generated and managed by MDA. Look for:
- `MDA-GENERATED-START` / `MDA-GENERATED-END` - Generated code sections
- `MDA-CUSTOM-START` / `MDA-CUSTOM-END` - Protected custom code sections