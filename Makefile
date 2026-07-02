.DEFAULT_GOAL := help
PYTHON := python
MANAGE := $(PYTHON) manage.py

.PHONY: help install run migrations migrate superuser shell test lint format collectstatic celery docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

run: ## Run the development server
	$(MANAGE) runserver 0.0.0.0:8000

migrations: ## Create new migrations
	$(MANAGE) makemigrations

migrate: ## Apply migrations
	$(MANAGE) migrate

superuser: ## Create a superuser
	$(MANAGE) createsuperuser

shell: ## Open the Django shell
	$(MANAGE) shell

test: ## Run the test suite
	pytest

lint: ## Lint the codebase
	ruff check .

format: ## Auto-format the codebase
	ruff format .

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --no-input

celery: ## Run a Celery worker
	celery -A config worker --loglevel=info

docker-up: ## Start docker-compose services
	docker compose up -d

docker-down: ## Stop docker-compose services
	docker compose down
