# PyPI Release Guide

Step-by-step instructions for publishing `pdf-autofillr-plugins` to PyPI.

---

## First-time setup

### 1. Create a PyPI account

Go to https://pypi.org/account/register/ and create an account.

Verify your email before continuing.

### 2. Enable 2FA (required by PyPI since 2024)

Go to https://pypi.org/manage/account/ and enable two-factor authentication.

### 3. Create an API token

Go to https://pypi.org/manage/account/token/

- Token name: `pdf-autofillr-plugins-publish`
- Scope: **Entire account** for first upload, then switch to project-scoped after first release
- Click **Add token** and copy it immediately — you won't see it again

### 4. Store the token

**Option A — `.pypirc` file (local machine)**

Create `~/.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-YOUR-TOKEN-HERE
```

```bash
chmod 600 ~/.pypirc
```

**Option B — Environment variable**

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-YOUR-TOKEN-HERE
```

**Option C — GitHub Actions secret (for CI)**

Go to your repo → Settings → Secrets and variables → Actions → New repository secret

- Name: `PYPI_API_TOKEN`
- Value: `pypi-YOUR-TOKEN-HERE`

---

## Releasing a new version

### Step 1 — Bump the version

Edit **both** of these files and change the version number:

```
packages/plugins/pyproject.toml
    version = "0.1.0"  →  "0.2.0"

packages/plugins/src/pdf_autofillr_plugins/__init__.py
    __version__ = "0.1.0"  →  "0.2.0"
```

Version format follows [Semantic Versioning](https://semver.org/):
- `MAJOR` — breaking changes to plugin interfaces (rare — would break all existing plugins)
- `MINOR` — new interfaces, new built-in plugins, backwards compatible
- `PATCH` — bug fixes to existing plugins or framework only

### Step 2 — Update CHANGELOG.md

Add an entry in `packages/plugins/CHANGELOG.md` and the root `CHANGELOG.md`:

```markdown
## [0.2.0] - 2026-05-15

### Added
- `PhoneValidatorPlugin` — E.164 phone number validation
- `DateValidatorPlugin` — date format and range validation

### Fixed
- `MLMapperPlugin` now handles None field values gracefully
```

### Step 3 — Run tests

```bash
cd packages/plugins
pip install -e ".[dev]"
pytest tests/ -v
```

All 112 tests must pass before releasing.

### Step 4 — Build the distribution

```bash
cd packages/plugins

# Install build tools if not already installed
pip install build twine

# Build source distribution + wheel
python -m build
```

This creates:
```
packages/plugins/dist/
├── pdf_autofillr_plugins-0.2.0.tar.gz
└── pdf_autofillr_plugins-0.2.0-py3-none-any.whl
```

### Step 5 — Check the distribution

```bash
twine check packages/plugins/dist/*
```

Fix any warnings before uploading.

### Step 6 — Upload to PyPI

```bash
twine upload packages/plugins/dist/*
```

If using `.pypirc` this will upload automatically.
If prompted: username is `__token__`, password is your API token.

### Step 7 — Verify on PyPI

```bash
# Wait ~60 seconds then install from PyPI to verify
pip install "pdf-autofillr-plugins==0.2.0" --force-reinstall

python -c "
from pdf_autofillr_plugins import PluginManager
print('pdf-autofillr-plugins installed correctly')
"
```

Check the PyPI page: https://pypi.org/project/pdf-autofillr-plugins/

### Step 8 — Tag the release

```bash
git add packages/plugins/pyproject.toml packages/plugins/src/pdf_autofillr_plugins/__init__.py
git add packages/plugins/CHANGELOG.md CHANGELOG.md
git commit -m "release: pdf-autofillr-plugins v0.2.0"
git tag plugins-v0.2.0
git push origin main --tags
```

---

## Automated release via GitHub Actions

After the first manual release, all future releases can be done by just pushing a tag.
The workflow at `.github/workflows/publish-pypi.yml` handles the rest.

```bash
# 1. Bump version + update CHANGELOG + commit
git commit -m "release: pdf-autofillr-plugins v0.2.0"

# 2. Tag and push — CI does the rest
git tag plugins-v0.2.0
git push origin main --tags
```

The workflow triggers on tags matching `plugins-v*`, builds the package, and publishes to PyPI automatically using the `PYPI_API_TOKEN` secret.

---

## Test PyPI (optional — for testing the release process)

Before publishing to the real PyPI, you can test on https://test.pypi.org/

```bash
# Upload to Test PyPI
twine upload --repository testpypi packages/plugins/dist/*

# Install from Test PyPI to verify
pip install --index-url https://test.pypi.org/simple/ pdf-autofillr-plugins

python -c "from pdf_autofillr_plugins import PluginManager; print('ok')"
```

---

## Version history

| Version | Date | PyPI |
|---------|------|------|
| 0.1.0 | 2026-04-30 | https://pypi.org/project/pdf-autofillr-plugins/0.1.0/ |

---

## Troubleshooting

**`Invalid distribution` error from twine check**

README.md has invalid Markdown. Run:
```bash
pip install readme-renderer
twine check dist/* --strict
```

**`File already exists` error from PyPI**

PyPI does not allow re-uploading the same version. Bump the version and rebuild.

**`403 Forbidden` from twine**

Your API token is wrong or expired. Generate a new one at https://pypi.org/manage/account/token/

**Package installs but imports fail**

Check the package name is correct — it's `pdf_autofillr_plugins` (with `r`, double `l`):
```python
from pdf_autofillr_plugins import PluginManager  # ✅ correct
from pdf_autofiller_plugins import PluginManager  # ✗ old name, wrong
```

**Adding a new built-in plugin — checklist before releasing**

- [ ] Plugin file created in `builtin/<category>/`
- [ ] Exported from `builtin/<category>/__init__.py`
- [ ] Unit tests in `tests/unit/test_builtin_plugins.py`
- [ ] Added to `tests/integration/test_all_plugins.py`
- [ ] Documented in `packages/plugins/README.md` and `USAGE.md`
- [ ] `CHANGELOG.md` entry added
- [ ] Version bumped in `pyproject.toml` and `__init__.py`
