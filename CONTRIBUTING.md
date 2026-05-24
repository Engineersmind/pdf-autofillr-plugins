# Contributing to pdf-autofillr-plugins

Thank you for your interest in contributing. This document covers everything you need to open a great pull request.

---

## Important Rules

- Never push directly to `main`
- All changes must go through Pull Requests
- Every contribution must start from a dedicated branch
- Commit messages must follow the convention below

---

## 1. Setup

```bash
git clone https://github.com/Engineersmind/pdf-autofillr-plugins.git
cd pdf-autofillr-plugins/plugins

python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

---

## 2. Branch Naming Convention

**Format:**

```
<type>/<module>-<short-description>
```

**Examples:**

```
feature/plugins-phone-validator
fix/plugins-email-validator-crash
docs/plugins-update-usage-guide
test/plugins-identity-mapper-edge-cases
chore/plugins-update-gitignore
```

**Allowed types:**

| Type | Use for |
|------|---------|
| `feature` | New plugin or functionality |
| `fix` | Bug fixes |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `chore` | Maintenance, config, tooling |
| `perf` | Performance improvements |
| `bug` | Reporting/fixing a confirmed bug |

```bash
git checkout main
git pull origin main
git checkout -b feature/plugins-phone-validator
```

---

## 3. Commit Convention

**Format:**

```
<type>/<module>: short description
```

**Examples:**

```bash
git commit -m "feature/plugins: add phone validator with E.164 support"
git commit -m "fix/plugins: email validator crash on None value"
git commit -m "docs/plugins: update USAGE.md with transformer examples"
git commit -m "test/plugins: add identity mapper edge case tests"
git commit -m "chore/plugins: update .gitignore"
```

**Allowed types:** `feature/` · `fix/` · `bug/` · `docs/` · `test/` · `chore/` · `perf/`

Any other format will be rejected by CI.

---

## 4. Running Tests

```bash
cd plugins
pytest tests/ -v --tb=short          # all 221 tests
pytest tests/unit/ -v                 # unit only
pytest tests/integration/ -v          # integration only
pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing
```

All 221 tests must pass before opening a PR.

---

## 5. Adding a New Built-in Plugin

1. Create `plugins/src/pdf_autofillr_plugins/builtin/<category>/<name>.py`
   - Inherit from the appropriate interface class
   - Decorate with `@plugin(category=..., name=...)`
   - Implement `get_metadata()` and all abstract methods
2. Export it from `plugins/src/pdf_autofillr_plugins/builtin/<category>/__init__.py`
3. Add unit tests in `plugins/tests/unit/`
4. Add to integration test in `plugins/tests/integration/test_all_plugins.py`
5. Document it in `plugins/README.md` and `plugins/USAGE.md`
6. Add a `plugins/CHANGELOG.md` entry

---

## 6. PR Checklist

- [ ] Branch named correctly — `<type>/<module>-<short-description>`
- [ ] All commit messages follow `<type>/<module>: description`
- [ ] PR title follows the same format
- [ ] No direct commits to `main`
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest tests/` passes locally (all 221 tests)
- [ ] New plugins have unit AND integration tests
- [ ] New built-ins exported from `builtin/<category>/__init__.py`
- [ ] `.env.example` updated if new env vars referenced
- [ ] `plugins/CHANGELOG.md` entry added
- [ ] `plugins/USAGE.md` updated if new plugin or interface added
- [ ] No build artifacts, `.env`, `__pycache__`, or `.egg-info` included

---

## 7. Releasing to PyPI

1. Bump `version` in `plugins/pyproject.toml` and `plugins/src/pdf_autofillr_plugins/__init__.py`
2. Add entry to `plugins/CHANGELOG.md`
3. Add entry to root `CHANGELOG.md`
4. Merge to `main` via PR
5. Push version tag — CI publishes to PyPI automatically

```bash
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
```

| Tag | PyPI package |
|-----|-------------|
| `plugins-v*` | pdf-autofillr-plugins |

---

## Questions?

Open an issue on the [repository](https://github.com/Engineersmind/pdf-autofillr-plugins).
