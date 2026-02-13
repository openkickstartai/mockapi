.PHONY: install test lint clean help

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install package in development mode
	pip install -e ".[dev]"

test: ## Run all tests with verbose output
	python -m pytest tests/ -v

lint: ## Run basic style checks
	python -m py_compile mockapi/server.py
	python -m py_compile mockapi/cli.py
	python -m py_compile mockapi/typegen.py

clean: ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true

serve: ## Start mockapi with example db (create db.json first)
	mockapi serve db.json
