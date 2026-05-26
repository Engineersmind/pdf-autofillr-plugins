# PyPI Release Guide — pdf-autofillr-plugins

Step-by-step instructions for publishing `pdf-autofillr-plugins` to PyPI.

---

## First-time setup

### 1. PyPI Trusted Publishing (recommended — no token needed)

The CI workflow uses OIDC Trusted Publishing — no API token is required for automated releases.

Set it up once at https://pypi.org/manage/account/publishing/:

- **Owner:** `Engineersmind`
- **Repository:** `pdf-autofillr-plugins`
- **Workflow:** `publish-pypi.yml`
- **Environment:** `pypi`

Then create the `pypi` environment in GitHub:
`https://github.com/Engineersmind/pdf-autofillr-plugins/settings/environments`

### 2. Manual release (twine — fallback)

```bash
pip install build twine
cd plugins && python -m build
twine upload dist/*
```

Use `__token__` as username and your PyPI API token as password.

---

## Release checklist

### Step 1 — Bump the version in two places

```
plugins/pyproject.toml
    version = "0.2.0"  →  "0.3.0"

plugins/src/pdf_autofillr_plugins/__init__.py
    __version__ = "0.2.0"  →  "0.3.0"
```

Version format: [Semantic Versioning](https://semver.org/)
- `MAJOR` — breaking changes to plugin interfaces (rare — would break all existing plugins)
- `MINOR` — new interfaces, new built-in plugins, backwards compatible
- `PATCH` — bug fixes only

### Step 2 — Update changelogs

Add an entry to `plugins/CHANGELOG.md`:

```markdown
## [0.3.0] - 2026-06-01

### Added
- `PhoneValidatorPlugin` — E.164 phone number validation

### Fixed
- `MLMapperPlugin` now handles None field values gracefully
```

Add a matching entry to the root `CHANGELOG.md` under `## [Unreleased]`.

### Step 3 — Run tests

```bash
cd plugins
pip install -e ".[dev]"
pytest tests/ -v
```

All tests must pass before releasing.

### Step 4 — Merge to main via PR

Follow the branch and commit conventions in [CONTRIBUTING.md](CONTRIBUTING.md).

### Step 5 — Push the version tag

```bash
git tag plugins-v0.3.0 && git push origin plugins-v0.3.0
```

CI will automatically:
1. Run all tests across Python 3.10–3.12
2. Verify `pyproject.toml` version matches the tag
3. Build the wheel and sdist
4. Publish to PyPI via Trusted Publishing (OIDC)
5. Update root `CHANGELOG.md` automatically

---

## Verify the release

```bash
# Wait ~60 seconds for PyPI to propagate
pip install "pdf-autofillr-plugins==0.3.0" --force-reinstall

python -c "
from pdf_autofillr_plugins import PluginManager, __version__
assert __version__ == '0.3.0', f'Wrong version: {__version__}'
print(f'pdf-autofillr-plugins {__version__} installed correctly ✅')
"
```

Check the PyPI page: https://pypi.org/project/pdf-autofillr-plugins/

---

## Test PyPI (optional)

```bash
twine upload --repository testpypi plugins/dist/*
pip install --index-url https://test.pypi.org/simple/ pdf-autofillr-plugins
```

---

## Version history

| Version | Date | PyPI |
|---------|------|------|
| 0.2.0 | 2026-05-24 | https://pypi.org/project/pdf-autofillr-plugins/0.2.0/ |
| 0.1.0 | 2026-04-30 | https://pypi.org/project/pdf-autofillr-plugins/0.1.0/ |

---

## Troubleshooting

**`File already exists` on PyPI** — PyPI does not allow re-uploading. Bump the version.

**`403 Forbidden` from twine** — API token wrong or expired. Regenerate at https://pypi.org/manage/account/token/

**Import fails after install** — Package name is `pdf_autofillr_plugins` (with double `l`):
```python
from pdf_autofillr_plugins import PluginManager  # ✅
from pdf_autofiller_plugins import PluginManager  # ✗ wrong
```

**Tests fail before release** — Run `pytest tests/ -v` from the `plugins/` directory and fix all failures before tagging.
