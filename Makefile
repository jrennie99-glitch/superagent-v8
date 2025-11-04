.PHONY: install test lint format clean docs run-api run-example benchmark help

help:
	@echo "SuperAgent - Makefile commands"
	@echo ""
	@echo "Development:"
	@echo "  make install     - Install dependencies and package"
	@echo "  make test        - Run test suite"
	@echo "  make lint        - Run linters (pylint, mypy)"
	@echo "  make format      - Format code with black and isort"
	@echo "  make clean       - Clean build artifacts"
	@echo ""
	@echo "Running:"
	@echo "  make run-api     - Start REST API server"
	@echo "  make run-example - Run basic usage example"
	@echo "  make benchmark   - Run performance benchmarks"
	@echo ""
	@echo "Documentation:"
	@echo "  make docs        - Generate documentation"

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ -v --cov=superagent --cov-report=html

test-fast:
	pytest tests/ -v -m "not slow and not benchmark"

lint:
	pylint superagent/
	mypy superagent/

format:
	black superagent/ tests/ examples/
	isort superagent/ tests/ examples/

clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf workspace/ example_workspace/ debug_example_project/

run-api:
	uvicorn superagent.api:app --reload --host 0.0.0.0 --port 8000

run-example:
	python examples/basic_usage.py

run-multi-agent:
	python examples/multi_agent_example.py

benchmark:
	pytest tests/test_performance.py -v -m benchmark

docs:
	@echo "Documentation in README.md and QUICKSTART.md"

setup-dev:
	pip install -r requirements.txt
	pip install -e .
	cp .env.example .env
	@echo "Setup complete! Edit .env to add your API keys"

check:
	black --check superagent/ tests/
	isort --check superagent/ tests/
	pylint superagent/
	mypy superagent/
	pytest tests/ -v

all: format lint test





