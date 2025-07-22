# Hello World API

This is a simple Hello World API built with FastAPI.

## Requirements

- Python 3.10+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- pytest
- uvicorn

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /hello`: Returns a simple greeting message.
- `POST /greetings`: Creates a new greeting message.

## Database

The application uses SQLite as the default database. You can configure the database connection using environment variables.

## Testing

```bash
pytest
```