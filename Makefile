.PHONY: help dev staging prod clean install migrate test docker-dev docker-full

help: ## Show this help message
	@echo "Available commands:"
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies using uv
	uv sync

dev: ## Start local development with hot reload
	@echo "🚀 Starting local development environment..."
	@cp .env.local .env
	@./scripts/dev.sh

dev-no-docker: ## Start local development without Docker (requires local PostgreSQL)
	@echo "🚀 Starting local development environment (no Docker)..."
	@cp .env.local .env
	@./scripts/dev-no-docker.sh

staging: ## Start staging environment
	@echo "🚀 Starting staging environment..."
	@cp .env.staging .env
	@./scripts/staging.sh

prod: ## Start production environment
	@echo "🚀 Starting production environment..."
	@cp .env.production .env
	@./scripts/prod.sh

docker-dev: ## Start only PostgreSQL in Docker for local development
	@echo "📦 Starting PostgreSQL container for development..."
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker-compose.dev.yml up -d; \
	else \
		./scripts/start-local-db.sh; \
	fi

docker-full: ## Start full application stack in Docker
	@echo "📦 Starting full application stack..."
	@cp .env.local .env
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose up --build; \
	else \
		echo "❌ docker-compose not available. Use 'make docker-dev' + 'make dev' instead"; \
	fi

migrate: ## Run database migrations
	uv run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	uv run alembic revision --autogenerate -m "$(MESSAGE)"

test: ## Run tests
	uv run pytest

clean: ## Clean up Docker containers and volumes
	@if command -v docker >/dev/null 2>&1; then \
		docker stop aipocket_postgres_dev 2>/dev/null || true; \
		docker rm aipocket_postgres_dev 2>/dev/null || true; \
		docker volume rm aipocket_postgres_data 2>/dev/null || true; \
		if command -v docker-compose >/dev/null 2>&1; then \
			docker-compose down -v 2>/dev/null || true; \
			docker-compose -f docker-compose.dev.yml down -v 2>/dev/null || true; \
		fi; \
	else \
		echo "Docker not available, skipping cleanup"; \
	fi

reset-db: ## Reset local database (removes all data!)
	@echo "⚠️  This will delete all local database data!"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ]
	@if command -v docker >/dev/null 2>&1; then \
		docker stop aipocket_postgres_dev 2>/dev/null || true; \
		docker rm aipocket_postgres_dev 2>/dev/null || true; \
		docker volume rm aipocket_postgres_data 2>/dev/null || true; \
		./scripts/start-local-db.sh; \
		sleep 5; \
		uv run alembic upgrade head; \
	else \
		echo "Docker not available. Please manually reset your local PostgreSQL database"; \
	fi

logs: ## Show application logs
	@if command -v docker-compose >/dev/null 2>&1; then \
		docker-compose logs -f app; \
	else \
		echo "docker-compose not available"; \
	fi

logs-db: ## Show database logs
	@if command -v docker >/dev/null 2>&1; then \
		docker logs -f aipocket_postgres_dev 2>/dev/null || echo "PostgreSQL container not running"; \
	else \
		echo "Docker not available"; \
	fi