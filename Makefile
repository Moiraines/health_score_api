.PHONY: help install dev test lint format check-format check-types check test-all db-shell db-backup db-restore clean docker-build docker-up docker-down docker-logs docker-bash docker-test docker-lint docker-format docker-check-format docker-check-types docker-test-all

# Project variables
PROJECT_NAME := health-score-api
DOCKER_COMPOSE := docker-compose -f docker-compose.yml -f docker-compose.override.yml
DOCKER_COMPOSE_PROD := docker-compose -f docker-compose.yml -f docker-compose.prod.yml
DOCKER_COMPOSE_TEST := docker-compose -f docker-compose.test.yml

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

# Help target
help:
	@echo '${YELLOW}Available commands:${RESET}'
	@echo ''
	@echo '${GREEN}Development:${RESET}'
	@echo '  ${WHITE}install${RESET}         - Install project dependencies'
	@echo '  ${WHITE}dev${RESET}            - Start development server with hot-reload'
	@echo '  ${WHITE}test${RESET}           - Run tests'
	@echo '  ${WHITE}lint${RESET}           - Run linters'
	@echo '  ${WHITE}format${RESET}         - Format code'
	@echo '  ${WHITE}check-format${RESET}    - Check code formatting'
	@echo '  ${WHITE}check-types${RESET}    - Check type annotations'
	@echo '  ${WHITE}test-all${RESET}       - Run all checks and tests'
	@echo ''
	@echo '${GREEN}Database:${RESET}'
	@echo '  ${WHITE}db-shell${RESET}       - Open database shell'
	@echo '  ${WHITE}db-backup${RESET}      - Create database backup'
	@echo '  ${WHITE}db-restore${RESET}     - Restore database from backup'
	@echo '  ${WHITE}db-migrate${RESET}     - Run database migrations'
	@echo '  ${WHITE}db-makemigrations${RESET} - Create new migration'
	@echo ''
	@echo '${GREEN}Docker:${RESET}'
	@echo '  ${WHITE}docker-build${RESET}   - Build Docker images'
	@echo '  ${WHITE}docker-up${RESET}      - Start all services'
	@echo '  ${WHITE}docker-down${RESET}    - Stop all services'
	@echo '  ${WHITE}docker-logs${RESET}    - View container logs'
	@echo '  ${WHITE}docker-bash${RESET}    - Open bash in API container'
	@echo '  ${WHITE}docker-test${RESET}    - Run tests in Docker'
	@echo '  ${WHITE}docker-lint${RESET}    - Run linters in Docker'
	@echo ''
	@echo '${GREEN}Production:${RESET}'
	@echo '  ${WHITE}prod-build${RESET}     - Build production images'
	@echo '  ${WHITE}prod-up${RESET}        - Start production services'
	@echo '  ${WHITE}prod-down${RESET}      - Stop production services'

# Development targets
install:
	@echo "${YELLOW}Installing dependencies...${RESET}"
	pip install -r requirements-dev.txt
	pre-commit install

dev:
	@echo "${YELLOW}Starting development server...${RESET}"
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "${YELLOW}Running tests...${RESET}"
	pytest -v --cov=app --cov-report=term-missing

lint:
	@echo "${YELLOW}Running linters...${RESET}"
	black --check .
	isort --check-only .
	flake8 .
	mypy .

format:
	@echo "${YELLOW}Formatting code...${RESET}"
	black .
	isort .

check-format:
	@echo "${YELLOW}Checking code formatting...${RESET}"
	black --check .
	isort --check-only .

check-types:
	@echo "${YELLOW}Checking type annotations...${RESET}"
	mypy .

test-all: check-format check-types lint test

# Database targets
db-shell:
	@echo "${YELLOW}Opening database shell...${RESET}"
	$(DOCKER_COMPOSE) exec db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2)

db-backup:
	@echo "${YELLOW}Creating database backup...${RESET}"
	@mkdir -p backups
	@$(DOCKER_COMPOSE) exec -T db pg_dump -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2) > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "${GREEN}Backup created successfully!${RESET}"

db-restore:
	@if [ -z "$(file)" ]; then \
		echo "${YELLOW}Please specify a backup file with file=path/to/backup.sql${RESET}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Restoring database from $(file)...${RESET}"
	@$(DOCKER_COMPOSE) exec -T db psql -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2) < $(file)
	@echo "${GREEN}Database restored successfully!${RESET}"

db-migrate:
	@echo "${YELLOW}Running database migrations...${RESET}"
	$(DOCKER_COMPOSE) run --rm api alembic upgrade head

db-makemigrations:
	@if [ -z "$(message)" ]; then \
		echo "${YELLOW}Please provide a message with message='Your migration message'${RESET}"; \
		exit 1; \
	fi
	@echo "${YELLOW}Creating new migration...${RESET}"
	$(DOCKER_COMPOSE) run --rm api alembic revision --autogenerate -m "$(message)"

# Docker targets
docker-build:
	@echo "${YELLOW}Building Docker images...${RESET}"
	$(DOCKER_COMPOSE) build

docker-up:
	@echo "${YELLOW}Starting services...${RESET}"
	$(DOCKER_COMPOSE) up -d

wait-for-db:
	@echo "${YELLOW}Waiting for database to be ready...${RESET}"
	@until $$(docker-compose exec -T db pg_isready -U $$(grep POSTGRES_USER .env | cut -d '=' -f2) -d $$(grep POSTGRES_DB .env | cut -d '=' -f2) > /dev/null 2>&1); do \
		echo "${YELLOW}Waiting for PostgreSQL...${RESET}"; \
		sleep 2; \
	done

docker-down:
	@echo "${YELLOW}Stopping services...${RESET}"
	$(DOCKER_COMPOSE) down

docker-logs:
	@echo "${YELLOW}Showing logs...${RESET}"
	$(DOCKER_COMPOSE) logs -f

docker-bash:
	@echo "${YELLOW}Opening bash in API container...${RESET}"
	$(DOCKER_COMPOSE) exec api bash

docker-test:
	@echo "${YELLOW}Running tests in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make test

docker-lint:
	@echo "${YELLOW}Running linters in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make lint

docker-format:
	@echo "${YELLOW}Formatting code in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make format

docker-check-format:
	@echo "${YELLOW}Checking code formatting in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make check-format

docker-check-types:
	@echo "${YELLOW}Checking type annotations in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make check-types

docker-test-all:
	@echo "${YELLOW}Running all checks and tests in Docker...${RESET}"
	$(DOCKER_COMPOSE) run --rm api make test-all

# Production targets
prod-build:
	@echo "${YELLOW}Building production images...${RESET}"
	$(DOCKER_COMPOSE_PROD) build

prod-up:
	@echo "${YELLOW}Starting production services...${RESET}"
	$(DOCKER_COMPOSE_PROD) up -d

prod-down:
	@echo "${YELLOW}Stopping production services...${RESET}"
	$(DOCKER_COMPOSE_PROD) down

# Cleanup
clean:
	@echo "${YELLOW}Cleaning up...${RESET}"
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	rm -rf .coverage htmlcov
	@echo "${GREEN}Cleanup complete!${RESET}"
