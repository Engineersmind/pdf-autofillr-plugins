# Changelog

All notable changes to `pdf-autofillr-plugins` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- `PhoneValidatorPlugin` — E.164 phone number validation
- `DateValidatorPlugin` — date format and range validation
- `ConfidenceFilterPlugin` — filters fields below a confidence threshold
- Plugin dependency resolution
- Plugin versioning and compatibility checks
- Plugin hot-reload in development mode

---

## [0.2.1] - 2026-05-27

### Added
- `loader/plugin_loader.py` — runtime loader for community plugin manifests from `registry/`
- `registry/` — community-submitted plugin manifests folder with `.gitkeep`
- `hooks/base_hooks.py` — full lifecycle hook system: `PreExtractHook`, `PostExtractHook`, `PreFillHook`, `PostFillHook`, and `HookRegistry`
- `plugin.schema.json` — JSON schema for validating community plugin manifests
- `ci.yml` — lint, type check (ruff, black, isort, mypy), and zero runtime dep check across Python 3.10/3.11/3.12
- `validate-plugins.yml` — manifest schema validation and API compatibility check on every PR
- `LLMAdapter` — flagship plugin interface for plugging in any LLM for field mapping
- `OutputFormatterPlugin` — plugin interface for custom output formatters
- `DataConnectorPlugin` — plugin interface for pulling data from CRMs/APIs/databases
- `LiteLLMAdapter` — production LLM adapter via LiteLLM (OpenAI, Anthropic, Ollama, Gemini, Bedrock, Groq)
- `NoOpLLMAdapter` — identity mapping adapter for testing
- `JSONReportFormatter` — wraps filled PDF in JSON report envelope
- `PassthroughFormatter` — returns filled PDF bytes as-is
- `DictConnector` — in-memory dict data connector for testing
- `JSONFileConnector` — JSON file data connector
- `.gitattributes` — enforces LF line endings across all Python, YAML, TOML, and Markdown files

### Changed
- `PluginRegistry` moved from `registry.py` into `registry/plugin_registry.py` to support community manifest folder
- `pyproject.toml` — moved ruff `select`/`ignore` from deprecated `[tool.ruff]` to `[tool.ruff.lint]`
- Bumped GitHub Actions — `checkout` v4→v6, `setup-python` v5→v6, `codeql-action/*` v3→v4, `upload-artifact` v4→v7, `download-artifact` v4→v8, `codecov/codecov-action` v4→v6

### Fixed
- All ruff lint errors resolved — import sorting (`I001`), blank line whitespace (`W293`), unused variable (`F841`), multiple statements on one line (`E701`)
- All black formatting applied across 67 source files — CRLF → LF conversion in CI to handle Windows/Linux line ending mismatch
- All mypy type errors resolved — `Optional[List[str]]` on `PluginMetadata` dataclass fields, `-> None` on `__init__` methods, `# type: ignore` for dynamic decorator attributes, `format_bytes` signature fixed

---

## [0.2.0] - 2026-05-24

### Added
- `pdf-autofillr-plugins` CLI entry point with `setup` and `status` commands
- `usage/` folder bundled inside the package — one guide per plugin type
  (extractor, mapper, validator, filler, chunker, embedder, transformer)
- `setup` command copies `configs/` samples and `usage/` guides to working directory
- `status` command checks module installation and env vars
- `MLMapperPlugin` — synonym-table mapper with 25+ built-in field name mappings, config-extensible
- `InvoiceExtractorPlugin` — extracts invoice_number, invoice_date, vendor_name, total_amount
- `validate_batch()` on `ValidatorPlugin` — validate multiple fields at once
- `get_mapping_confidence()` on both `IdentityMapperPlugin` and `MLMapperPlugin`
- `MANIFEST.in` includes `usage/*.md` in sdist

### Changed
- Bumped `requires-python` to `>=3.10` (aligns with SDK and CLI)
- Updated `pyproject.toml`: corrected author to `Engineers Mind / Support@pdffillr.ai`, updated repo URLs
- Build backend updated to `setuptools>=77.0`
- `@plugin` decorator now falls back to class docstring for description
- `PluginManager.find_extractor()` and `find_mapper()` now sort by priority descending (higher = wins)

### Fixed
- `PluginRegistry._discover_from_path()` now skips files starting with `_` (was causing import errors on `__init__.py`)
- `PluginManager.unload_plugin()` correctly resets `_initialized` flag so re-load works cleanly

---

## [0.1.0] - 2026-04-30

### Added
- Initial release of the plugin framework as a standalone PyPI package
- `PluginRegistry` — discovers and registers plugin classes from file paths or module paths
- `PluginManager` — loads, initialises, caches, and shuts down plugins; lazy loading by default
- `@plugin` decorator — stamps metadata onto a class so the registry can find it
- `@requires` decorator — declares plugin dependencies
- 8 plugin interfaces: `BasePlugin`, `ExtractorPlugin`, `MapperPlugin`, `ValidatorPlugin`,
  `FillerPlugin`, `ChunkerPlugin`, `EmbedderPlugin`, `TransformerPlugin`
- 3 built-in plugins:
  - `EmailValidatorPlugin` — validates email format, length, disposable domains, and custom rules
  - `PassthroughExtractorPlugin` — returns pre-configured fields unchanged; useful for testing
  - `IdentityMapperPlugin` — maps fields by exact match then snake_case normalisation
- `pdf_autofillr_plugins.utils` — common helpers: hashing, JSON, retry, Timer, string utils
- `pdf_autofillr_plugins.core` — HandlerInterface, StorageInterface cross-module abstractions
- 221 tests (unit + integration), all passing
- Benchmarking suite for plugin performance across 6 document domains
- Docker deployment configuration
- GitHub Actions CI (test + PyPI publish)
- Full docs: `README.md`, `USAGE.md`, `quickstart.md`