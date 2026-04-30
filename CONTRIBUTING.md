# Contributing to pdf-autofillr-plugins

## Setup

```bash
git clone https://github.com/Engineersmind/pdf-autofillr-plugins.git
cd pdf-autofillr-plugins/packages/plugins
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
```

## Tests

```bash
pytest tests/ -v                                              # all 112 tests
pytest tests/unit/ -v                                         # unit only
pytest tests/integration/ -v                                  # integration only
pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing
```

## Branches

| Branch | Purpose |
|--------|---------|
| `main` | Stable — never push directly |
| `dev`  | All PRs merge here |
| `feature/<name>` | New plugin or feature |
| `fix/<name>` | Bug fixes |

## PR checklist

- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest tests/` passes (all 112 tests)
- [ ] New plugins have unit AND integration tests
- [ ] New built-ins exported from `builtin/__init__.py`
- [ ] `CHANGELOG.md` entry added
- [ ] `packages/plugins/USAGE.md` updated if new plugin added

## Adding a new built-in plugin

1. Create `packages/plugins/src/pdf_autofillr_plugins/builtin/<category>/<name>.py`
2. Export it from `packages/plugins/src/pdf_autofillr_plugins/builtin/<category>/__init__.py`
3. Add unit tests in `packages/plugins/tests/unit/`
4. Add to integration test in `packages/plugins/tests/integration/test_all_plugins.py`
5. Document it in `packages/plugins/README.md` and `packages/plugins/USAGE.md`

## Releasing to PyPI

1. Bump `version` in `packages/plugins/pyproject.toml` and `__init__.py`
2. Add entry to `packages/plugins/CHANGELOG.md` and root `CHANGELOG.md`
3. Merge to `main`
4. Push version tag — CI publishes to PyPI automatically

```bash
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
```

| Tag | PyPI package |
|-----|-------------|
| `plugins-v0.1.0` | pdf-autofillr-plugins |
