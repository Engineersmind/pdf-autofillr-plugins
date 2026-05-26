# Changelog

All notable changes to the **pdf-autofillr-plugins** repository are documented here.
Each release also has an entry in `plugins/CHANGELOG.md`.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## Packages

| Package | Latest | Changelog |
|---------|--------|-----------|
| pdf-autofillr-plugins | 0.2.0 | [plugins/CHANGELOG.md](plugins/CHANGELOG.md) |

---

## [Unreleased]

### Planned
- `PhoneValidatorPlugin` — E.164 phone number validation
- `DateValidatorPlugin` — date format and range validation
- `ConfidenceFilterPlugin` — filters fields below a configurable confidence threshold
- Plugin dependency resolution and compatibility checks
- Plugin hot-reload in development mode
- Shell completion for `pdf-autofillr-plugins` CLI

---

## [plugins-0.2.0] — 2026-05-24

### Added
- `pr-conventions.yml` — enforces branch naming, commit message, PR title, and CHANGELOG conventions
- `update-changelog.yml` — auto-updates root CHANGELOG.md on release tag push
- `codeql.yml` — weekly CodeQL security scan on `plugins/src`
- `dependabot.yml` — weekly dependency updates (security/major only, grouped)
- `CODEOWNERS` — all 3 maintainers required on every PR
- `BRANCH_PROTECTION_SETUP.md` — step-by-step guide for `main` branch protection
- `CONTRIBUTING_DEV.md` — internal dev guide with release process
- `SECURITY.md` — vulnerability disclosure policy aligned with SDK and CLI repos
- `pat_plugins.txt` in `.gitignore` — for PAT documentation file
- `CHANGELOG_BOT_TOKEN` fallback to `GITHUB_TOKEN` in changelog workflow
- `usage/` guides directory bundled in package (one guide per plugin type)
- `pdf-autofillr-plugins setup` and `pdf-autofillr-plugins status` CLI entry points

### Changed
- `tests.yml` now triggers on push to non-`main` branches (not `main` + PRs) — consistent with SDK pattern
- `publish-pypi.yml` now runs tests, verifies version matches tag, then builds — consistent with SDK/CLI
- Updated `pyproject.toml`: bumped version to 0.2.0, corrected author/email, updated URLs to correct repo
- Updated `CONTRIBUTING.md` to match SDK/CLI branch and commit conventions
- `CODEOWNERS` updated to individual GitHub handles (replaces team slug)
- Bumped `requires-python` to `>=3.10` (aligns with SDK and CLI)

### Fixed
- `publish-pypi.yml` now verifies `pyproject.toml` version matches git tag before publishing
- `tests.yml` now uses `working-directory: plugins` (not `cd plugins` inline) for consistency

---

## [plugins-0.1.0] — 2026-04-30

### Added
- Initial release of `pdf-autofillr-plugins`
- `PluginRegistry` — discovers and registers plugin classes from file paths or module paths
- `PluginManager` — loads, caches, and shuts down plugins; lazy loading by default
- `@plugin` decorator — stamps metadata onto a class for registry discovery
- `@requires` decorator — declares plugin pip dependencies
- 8 plugin interfaces: `BasePlugin`, `ExtractorPlugin`, `MapperPlugin`, `ValidatorPlugin`,
  `FillerPlugin`, `ChunkerPlugin`, `EmbedderPlugin`, `TransformerPlugin`
- 5 built-in plugins: `EmailValidatorPlugin`, `PassthroughExtractorPlugin`,
  `InvoiceExtractorPlugin`, `IdentityMapperPlugin`, `MLMapperPlugin`
- `pdf_autofillr_plugins.utils` — common helpers: hashing, JSON, retry, Timer, string utils
- `pdf_autofillr_plugins.core` — HandlerInterface, StorageInterface cross-module abstractions
- 112 tests (unit + integration), all passing
- Benchmarking suite (6 document domains)
- Docker deployment configuration
- GitHub Actions CI (tests + PyPI publish)
