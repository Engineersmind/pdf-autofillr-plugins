# pdf-autofillr-plugins — Makefile

.PHONY: help install test test-unit test-integration test-coverage benchmark build clean

help:
	@echo ""
	@echo "pdf-autofillr-plugins"
	@echo "====================="
	@echo "  install          pip install -e .[dev]"
	@echo "  test             run all 221 tests"
	@echo "  test-unit        unit tests only"
	@echo "  test-integration integration tests only"
	@echo "  test-coverage    run with coverage report"
	@echo "  benchmark        run plugin performance benchmarks"
	@echo "  build            build distribution packages"
	@echo "  clean            remove build artefacts"
	@echo ""

install:
	cd plugins && pip install -e ".[dev]"

test:
	cd plugins && pytest tests/ --tb=short -q

test-unit:
	cd plugins && pytest tests/unit/ -v

test-integration:
	cd plugins && pytest tests/integration/ -v

test-coverage:
	cd plugins && pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing

benchmark:
	python benchmarks/run_benchmark.py

build:
	cd plugins && pip install build && python -m build

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
