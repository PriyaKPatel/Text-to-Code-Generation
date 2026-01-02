.PHONY: help install test lint format build run deploy-local deploy-aws clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linting"
	@echo "  make format        - Format code with black"
	@echo "  make build         - Build Docker image"
	@echo "  make run           - Run locally with Docker"
	@echo "  make deploy-local  - Deploy locally"
	@echo "  make deploy-aws    - Deploy to AWS"
	@echo "  make clean         - Clean up generated files"

install:
	pip install -r requirements.txt
	pip install black flake8 mypy pytest-cov

test:
	pytest tests/ -v --cov=app --cov-report=term-missing

lint:
	flake8 app/ tests/ --max-line-length=120
	mypy app/ --ignore-missing-imports

format:
	black app/ tests/

build:
	docker build -t text-to-code:latest .

run:
	docker-compose up -d

deploy-local:
	chmod +x scripts/deploy-local.sh
	./scripts/deploy-local.sh

deploy-aws:
	chmod +x scripts/deploy-aws.sh
	./scripts/deploy-aws.sh

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	docker-compose down
	docker system prune -f
