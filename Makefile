# MDA Project Makefile

.PHONY: help test test-unit test-integration test-e2e test-all clean install

help:
	@echo "MDA Project Commands:"
	@echo "  make install          - Install dependencies"
	@echo "  make test            - Run all tests"
	@echo "  make test-unit       - Run unit tests only (no API key needed)"
	@echo "  make test-integration - Run integration tests (requires API key)"
	@echo "  make test-e2e        - Run end-to-end tests"
	@echo "  make test-structure  - Run structure tests only"
	@echo "  make clean           - Clean generated files"
	@echo "  make run-example     - Run example PIM conversion"

install:
	cd pim-engine && pip install -r requirements.txt

test: test-all

test-all:
	@echo "Running all tests..."
	cd pim-engine && python -m pytest tests/ -v

test-unit:
	@echo "Running unit tests (no API key required)..."
	cd pim-engine && python tests/test_suite.py --no-integration

test-integration:
	@echo "Running integration tests (requires GEMINI_API_KEY)..."
	cd pim-engine && python -m pytest tests/test_mda_e2e.py -v

test-e2e:
	@echo "Running end-to-end tests..."
	cd pim-engine && python -m pytest tests/test_mda_e2e.py::TestMDAEndToEnd -v

test-structure:
	@echo "Running structure tests..."
	cd pim-engine && python -m pytest tests/converters/test_converters_structure.py -v

test-orchestrator:
	@echo "Running orchestrator tests..."
	cd pim-engine && python -m pytest tests/test_mda_orchestrator.py -v

clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*_psm_*.yaml" -delete
	find . -type d -name "*_generated" -exec rm -rf {} +
	find . -type d -name "*_fastapi_generated" -exec rm -rf {} +
	rm -rf pim-engine/.pytest_cache
	rm -rf pim-engine/htmlcov
	rm -rf pim-engine/.coverage

run-example:
	@echo "Running example PIM conversion..."
	@if [ -f ".env" ] && grep -q "GEMINI_API_KEY" .env; then \
		python mda.py pim-engine/models/图书管理系统.md --platform fastapi --no-deploy; \
	else \
		echo "Error: Please set GEMINI_API_KEY in .env file"; \
		echo "Copy .env.example to .env and add your API key"; \
		exit 1; \
	fi

coverage:
	@echo "Running tests with coverage..."
	cd pim-engine && python -m pytest tests/ --cov=src --cov-report=html --cov-report=term

lint:
	@echo "Running linters..."
	cd pim-engine && flake8 src/ tests/ --max-line-length=100
	cd pim-engine && mypy src/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	cd pim-engine && black src/ tests/

check: lint test-unit
	@echo "All checks passed!"

# Development helpers
dev-setup: install
	@echo "Setting up development environment..."
	@if [ ! -f ".env" ]; then \
		cp .env.example .env; \
		echo "Created .env file - please add your GEMINI_API_KEY"; \
	fi

watch-test:
	@echo "Watching for changes and running tests..."
	cd pim-engine && python -m pytest tests/converters/test_converters_structure.py -v --watch