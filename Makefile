
.PHONY: run test lint format

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload  # dev server

test:
	pytest -q  # run tests

lint:
	ruff check .  # lint

format:
	ruff check --fix .  # quick fixes
