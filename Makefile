.PHONY: help up down logs migrate migrate-down seed test test-api test-web quality fmt clean reset

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)RaptorFlow Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ======================================
# Docker Compose Commands
# ======================================

up: ## Start all services (Docker Compose)
	@echo "$(BLUE)Starting all services...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services started$(NC)"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"

down: ## Stop all services
	@echo "$(BLUE)Stopping all services...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View API logs only
	docker-compose logs -f api

logs-web: ## View frontend logs only
	docker-compose logs -f web

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Services restarted$(NC)"

ps: ## Show running containers
	docker-compose ps

# ======================================
# Database Commands
# ======================================

migrate: ## Run database migrations
	@echo "$(BLUE)Running migrations...$(NC)"
	cd apps/api && alembic upgrade head
	@echo "$(GREEN)✓ Migrations applied$(NC)"

migrate-down: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	cd apps/api && alembic downgrade -1
	@echo "$(GREEN)✓ Migration rolled back$(NC)"

migrate-create: ## Create a new migration (use: make migrate-create NAME="add users table")
	@echo "$(BLUE)Creating migration: $(NAME)$(NC)"
	cd apps/api && alembic revision -m "$(NAME)"

migrate-history: ## Show migration history
	cd apps/api && alembic history

seed: ## Seed database with sample data
	@echo "$(BLUE)Seeding database...$(NC)"
	cd apps/api && python scripts/seed_local.py
	@echo "$(GREEN)✓ Database seeded$(NC)"

db-shell: ## Open PostgreSQL shell
	docker-compose exec db psql -U raptorflow -d raptorflow_dev

redis-cli: ## Open Redis CLI
	docker-compose exec redis redis-cli

# ======================================
# Testing Commands
# ======================================

test: ## Run all tests (API + Web)
	@echo "$(BLUE)Running all tests...$(NC)"
	@make test-api
	@make test-web
	@echo "$(GREEN)✓ All tests passed$(NC)"

test-api: ## Run API tests
	@echo "$(BLUE)Running API tests...$(NC)"
	cd apps/api && pytest -v --cov=. --cov-report=term-missing

test-web: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd apps/web && npm test -- --coverage

test-e2e: ## Run E2E tests
	@echo "$(BLUE)Running E2E tests...$(NC)"
	cd apps/web && npm run test:e2e

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	cd apps/web && npm run test:watch

# ======================================
# Quality Checks
# ======================================

quality: ## Run all quality checks (lint + typecheck + test)
	@echo "$(BLUE)Running quality checks...$(NC)"
	@make quality-api
	@make quality-web
	@echo "$(GREEN)✓ All quality checks passed$(NC)"

quality-api: ## Run API quality checks
	@echo "$(BLUE)Checking API quality...$(NC)"
	cd apps/api && ruff check . && ruff format --check . && mypy . && pytest
	@echo "$(GREEN)✓ API quality checks passed$(NC)"

quality-web: ## Run frontend quality checks
	@echo "$(BLUE)Checking frontend quality...$(NC)"
	cd apps/web && npm run type-check && npm run lint && npm run format:check && npm test
	@echo "$(GREEN)✓ Frontend quality checks passed$(NC)"

lint: ## Run linters only
	@echo "$(BLUE)Running linters...$(NC)"
	cd apps/api && ruff check .
	cd apps/web && npm run lint

lint-fix: ## Fix auto-fixable lint issues
	@echo "$(BLUE)Fixing lint issues...$(NC)"
	cd apps/api && ruff check --fix .
	cd apps/web && npm run lint:fix

fmt: ## Format all code
	@echo "$(BLUE)Formatting code...$(NC)"
	cd apps/api && ruff format .
	cd apps/web && npm run format:write
	@echo "$(GREEN)✓ Code formatted$(NC)"

typecheck: ## Run type checkers
	@echo "$(BLUE)Type checking...$(NC)"
	cd apps/api && mypy .
	cd apps/web && npm run type-check
	@echo "$(GREEN)✓ Type checking passed$(NC)"

# ======================================
# Development Commands
# ======================================

dev-api: ## Start API in development mode
	@echo "$(BLUE)Starting API (hot reload)...$(NC)"
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-web: ## Start frontend in development mode
	@echo "$(BLUE)Starting frontend (hot reload)...$(NC)"
	cd apps/web && npm run dev

dev-worker: ## Start worker in development mode
	@echo "$(BLUE)Starting worker...$(NC)"
	cd apps/worker && celery -A app.worker worker --loglevel=info

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	cd apps/api && pip install -r requirements.txt -r requirements-dev.txt
	cd apps/web && npm install
	@echo "$(GREEN)✓ Dependencies installed$(NC)"

# ======================================
# Build Commands
# ======================================

build: ## Build all containers
	@echo "$(BLUE)Building containers...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Containers built$(NC)"

build-api: ## Build API container only
	docker-compose build api

build-web: ## Build frontend container only
	docker-compose build web

# ======================================
# Cleanup Commands
# ======================================

clean: ## Remove build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".next" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(NC)"

reset: ## ⚠️  DANGER: Reset database and volumes (deletes ALL data)
	@echo "$(RED)WARNING: This will delete ALL data!$(NC)"
	@read -p "Are you sure? Type 'yes' to continue: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "$(BLUE)Resetting everything...$(NC)"; \
		docker-compose down -v; \
		docker-compose up -d db redis; \
		sleep 5; \
		make migrate; \
		make seed; \
		echo "$(GREEN)✓ Reset complete$(NC)"; \
	else \
		echo "$(YELLOW)Aborted$(NC)"; \
	fi

# ======================================
# CI/CD Commands
# ======================================

ci: ## Run CI checks locally (same as GitHub Actions)
	@echo "$(BLUE)Running CI checks...$(NC)"
	./scripts/run-quality-checks.sh
	@echo "$(GREEN)✓ CI checks passed$(NC)"

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	@make lint-fix
	@make typecheck
	@make test
	@echo "$(GREEN)✓ Ready to commit!$(NC)"

# ======================================
# Documentation Commands
# ======================================

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving docs at http://localhost:8080$(NC)"
	cd docs && python -m http.server 8080

docs-api: ## Generate API documentation
	@echo "$(BLUE)Generating API docs...$(NC)"
	cd apps/api && python scripts/generate_openapi.py > openapi.json
	@echo "$(GREEN)✓ API docs generated at apps/api/openapi.json$(NC)"

# ======================================
# Deployment Commands
# ======================================

deploy-staging: ## Deploy to staging (requires GCP auth)
	@echo "$(BLUE)Deploying to staging...$(NC)"
	gcloud builds submit --config=.cloudbuild/quality-gates.yaml
	@echo "$(GREEN)✓ Deployed to staging$(NC)"

deploy-prod: ## Deploy to production (requires manual approval)
	@echo "$(RED)Production deployment requires manual approval in GitHub Actions$(NC)"
	@echo "Push a tag to trigger: git tag v1.0.0 && git push origin v1.0.0"

# ======================================
# Security Commands
# ======================================

security-scan: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	cd apps/api && bandit -r . -f json -o bandit-report.json || true
	cd apps/api && safety check || true
	cd apps/web && npm audit || true
	@echo "$(GREEN)✓ Security scan complete$(NC)"

secrets-check: ## Check for accidentally committed secrets
	@echo "$(BLUE)Checking for secrets...$(NC)"
	@if git log -p | grep -i "password\|api_key\|secret" | grep -v ".gitignore\|.env.example"; then \
		echo "$(RED)⚠️  Potential secrets found in commit history!$(NC)"; \
	else \
		echo "$(GREEN)✓ No secrets found$(NC)"; \
	fi

# ======================================
# Utility Commands
# ======================================

shell-api: ## Open shell in API container
	docker-compose exec api /bin/bash

shell-web: ## Open shell in frontend container
	docker-compose exec web /bin/sh

version: ## Show version info
	@echo "$(BLUE)RaptorFlow Version Info$(NC)"
	@echo "Git Branch: $$(git rev-parse --abbrev-ref HEAD)"
	@echo "Git Commit: $$(git rev-parse --short HEAD)"
	@echo "Python: $$(python --version 2>&1)"
	@echo "Node: $$(node --version)"
	@echo "Docker: $$(docker --version)"

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@curl -sf http://localhost:8000/health > /dev/null && echo "$(GREEN)✓ API: healthy$(NC)" || echo "$(RED)✗ API: unhealthy$(NC)"
	@curl -sf http://localhost:3000 > /dev/null && echo "$(GREEN)✓ Web: healthy$(NC)" || echo "$(RED)✗ Web: unhealthy$(NC)"
	@docker-compose exec db pg_isready -U raptorflow > /dev/null && echo "$(GREEN)✓ Database: healthy$(NC)" || echo "$(RED)✗ Database: unhealthy$(NC)"
	@docker-compose exec redis redis-cli ping > /dev/null && echo "$(GREEN)✓ Redis: healthy$(NC)" || echo "$(RED)✗ Redis: unhealthy$(NC)"
