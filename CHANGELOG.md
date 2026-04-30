# Changelog

All notable changes to the **pdf-autofillr-plugins** repository are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [0.1.0] - 2026-04-30

### Added
- Initial release of `pdf-autofillr-plugins`
- `PluginRegistry` — discovers and registers plugin classes from file paths or module paths
- `PluginManager` — loads, caches, and shuts down plugins; lazy loading by default
- `@plugin` decorator — stamps metadata onto a class for registry discovery
- `@requires` decorator — declares plugin pip dependencies
- 8 plugin interfaces: `BasePlugin`, `ExtractorPlugin`, `MapperPlugin`, `ValidatorPlugin`,
  `FillerPlugin`, `ChunkerPlugin`, `EmbedderPlugin`, `TransformerPlugin`
- 5 built-in plugins:
  - `EmailValidatorPlugin` — email format, length, disposable domain, custom rules
  - `PassthroughExtractorPlugin` — returns pre-configured fields; testing helper
  - `InvoiceExtractorPlugin` — extracts invoice_number, invoice_date, vendor_name, total_amount
  - `IdentityMapperPlugin` — exact + snake_case normalised schema mapping
  - `MLMapperPlugin` — synonym-table mapper with 25+ built-in mappings, config-extensible
- `pdf_autofillr_plugins.utils` — common helpers: hashing, JSON, retry, Timer, string utils
- `pdf_autofillr_plugins.core` — HandlerInterface, StorageInterface cross-module abstractions
- 112 tests (unit + integration), all passing
- Benchmarking suite for plugin performance across 6 document domains
- Docker deployment configuration
- GitHub Actions CI (test + PyPI publish)
- Full docs: `README.md`, `USAGE.md`, `quickstart.md`
