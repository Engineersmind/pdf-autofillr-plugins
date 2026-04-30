# Changelog

All notable changes to `pdf-autofillr-plugins` are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-04-30

### Added
- Initial release of the plugin framework as a standalone PyPI package
- `PluginRegistry` — discovers and registers plugin classes from file paths or module paths
- `PluginManager` — loads, initialises, caches, and shuts down plugins; lazy loading by default
- `@plugin` decorator — marks a class as a plugin with metadata (category, name, version, priority, tags)
- `@requires` decorator — declares plugin dependencies
- 8 plugin interfaces: `BasePlugin`, `ExtractorPlugin`, `MapperPlugin`, `ValidatorPlugin`, `FillerPlugin`, `ChunkerPlugin`, `EmbedderPlugin`, `TransformerPlugin`
- 3 built-in plugins:
  - `EmailValidatorPlugin` — validates email format, length, disposable domains, and custom rules
  - `PassthroughExtractorPlugin` — returns pre-configured fields unchanged; useful for testing
  - `IdentityMapperPlugin` — maps fields by exact match then snake_case normalisation
- `pdf-autofillr-plugins` entry in `pdf-autofillr plugins list`
- Examples: `custom_validator.py`, `custom_extractor.py`
- Full test suite: 64 tests across unit and integration

---

## Unreleased

### Planned
- `PhoneValidatorPlugin` — E.164 phone number validation
- `DateValidatorPlugin` — date format and range validation
- `ConfidenceFilterPlugin` — filters fields below a confidence threshold
- Plugin dependency resolution
- Plugin versioning and compatibility checks
- Plugin hot-reload in development mode
