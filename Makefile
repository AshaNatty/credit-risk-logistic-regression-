.PHONY: install test lint run docker-build docker-up docker-down clean

install:
	pip install -r requirements.txt

test:
	PYTHONPATH=. pytest tests/ -v --asyncio-mode=auto

lint:
	ruff check src/ tests/ || true
	mypy src/ --ignore-missing-imports || true

run:
	PYTHONPATH=. uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -f docker/Dockerfile -t agentic-ai-core-framework:latest .

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
