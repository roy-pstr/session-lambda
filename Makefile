
install:
	poetry install

test:
	poetry run pytest --cov=session_lambda

.PHONY: install test