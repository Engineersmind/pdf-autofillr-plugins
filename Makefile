# pdf-autofillr-plugins — Makefile

.PHONY: help install test test-unit test-integration test-coverage benchmark build publish clean

help:
	@echo ""
	@echo "pdf-autofillr-plugins"
	@echo "====================="
	@echo "  install          pip install -e .[dev]"
	@echo "  test             run all 112 tests"
	@echo "  test-unit        unit tests only"
	@echo "  test-integration integration tests only"
	@echo "  benchmark        run plugin performance benchmarks"
	@echo "  build            build distribution packages"
	@echo "  publish          upload to PyPI"
	@echo "  clean            remove build artefacts"
	@echo ""

install:
	cd packages/plugins && pip install -e ".[dev]"

test:
	cd packages/plugins && pytest tests/ -v

test-unit:
	cd packages/plugins && pytest tests/unit/ -v

test-integration:
	cd packages/plugins && pytest tests/integration/ -v

test-coverage:
	cd packages/plugins && pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing

benchmark:
	python benchmarks/run_benchmark.py

build:
	cd packages/plugins && pip install build && python -m build

publish:
	cd packages/plugins && twine upload dist/*

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"
