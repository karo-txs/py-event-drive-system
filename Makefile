# Makefile para dev-event-driven-system

.PHONY: api tests lint fmt coverage compose-up compose-down

venv:
	uv venv
	uv pip install -r pyproject.toml --extra dev

tests:
	set PYTHONPATH=$(CURDIR) && uv run pytest

lint:
	ruff check app tests

fmt:
	ruff format app tests

coverage:
    .venv\Scripts\coverage run -m pytest
    .venv\Scripts\coverage report
    .venv\Scripts\coverage xml

compose-up:
	docker compose -f docker/docker-compose.yml up -d

compose-down:
	docker compose -f docker/docker-compose.yml down
