# MDA-GENERATED-START: makefile
.PHONY: help install run test docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run the service locally"
	@echo "  make test         - Run tests"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start services with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose services"
	@echo "  make clean        - Clean up generated files"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f user-service

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf *.egg-info
	rm -rf dist/
	rm -rf build/

db-init:
	docker-compose up -d postgres
	sleep 5
	docker-compose exec postgres psql -U postgres -d userdb -f /docker-entrypoint-initdb.d/init_db.sql

format:
	black app/ tests/
	isort app/ tests/

lint:
	flake8 app/ tests/
	mypy app/
# MDA-GENERATED-END: makefile