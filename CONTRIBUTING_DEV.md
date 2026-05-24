# Developer Guide — pdf-autofillr-plugins

Internal reference for the Engineersmind team. Covers local setup, testing, and the release process.

---

## Repository Layout

```
pdf-autofillr-plugins/
├── plugins/                → pdf-autofillr-plugins package (source of truth)
│   ├── src/pdf_autofillr_plugins/
│   ├── tests/
│   ├── pyproject.toml
│   └── CHANGELOG.md
├── benchmarks/             → plugin performance suite (6 document domains)
├── deployment/             → Docker configs
├── docs/                   → architecture and guides
└── examples/               → top-level usage examples
```

---

## Local Setup

```bash
git clone https://github.com/Engineersmind/pdf-autofillr-plugins.git
cd pdf-autofillr-plugins/plugins

python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
```

---

## Running Tests

```bash
cd plugins
pytest tests/ -v --tb=short
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/ --cov=src/pdf_autofillr_plugins --cov-report=term-missing
```

---

## Branch Reference

| Branch | Purpose |
|--------|---------|
| `main` | Stable — never push directly |
| `feature/plugins-<name>` | New plugin or feature |
| `fix/plugins-<name>` | Bug fixes |
| `docs/plugins-<name>` | Documentation only |
| `test/plugins-<name>` | Test additions |
| `chore/plugins-<name>` | Maintenance / tooling |
| `perf/plugins-<name>` | Performance improvements |

**Nobody pushes directly to `main`** — no exceptions for internal team.

---

## PR Checklist

- [ ] `pip install -e ".[dev]"` succeeds cleanly
- [ ] `pytest tests/` passes with no failures
- [ ] New behaviour has test coverage
- [ ] `.env.example` updated if new env vars added
- [ ] `plugins/CHANGELOG.md` entry added
- [ ] Root `README.md` updated if new built-in plugin added
- [ ] No build artifacts, `.env`, `__pycache__`, or `.egg-info` committed

---

## Release Process

### Steps

1. Bump `version` in `plugins/pyproject.toml` and `plugins/src/pdf_autofillr_plugins/__init__.py`
2. Add an entry to `plugins/CHANGELOG.md`
3. Update the packages table in root `CHANGELOG.md`
4. Merge to `main` via PR
5. Push the version tag — CI publishes to PyPI automatically

### Current versions

| Tag | PyPI package | Version |
|-----|-------------|---------|
| `plugins-v*` | pdf-autofillr-plugins | **0.2.0** |

### Tagging a release

```bash
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
```

CI will:
1. Run all tests across Python 3.10–3.12
2. Verify `pyproject.toml` version matches the tag
3. Build the wheel and sdist
4. Publish to PyPI via Trusted Publishing (OIDC)
5. Update root `CHANGELOG.md` automatically

---

## PyPI Trusted Publishing Setup

Before the first release, set up Trusted Publishing on PyPI:

1. Go to https://pypi.org/manage/account/publishing/
2. Add a new publisher:
   - **Owner**: `Engineersmind`
   - **Repository**: `pdf-autofillr-plugins`
   - **Workflow**: `publish-pypi.yml`
   - **Environment**: `pypi`
3. On GitHub, create the `pypi` environment at:
   `https://github.com/Engineersmind/pdf-autofillr-plugins/settings/environments`

---

## CHANGELOG_BOT_TOKEN Secret

The `update-changelog.yml` workflow uses `CHANGELOG_BOT_TOKEN` to push back to `main` after a release tag.
If not set, it falls back to `GITHUB_TOKEN` (which works unless `main` is branch-protected).

Set this up at:
`https://github.com/Engineersmind/pdf-autofillr-plugins/settings/secrets/actions`

Use a fine-grained PAT with **Contents: write** permission on this repo only.
Document the token in `pat_plugins.txt` (already in `.gitignore`).

---

## Adding a New `.env` Variable

1. Add it to `plugins/.env.example` with a comment explaining it
2. Document it in `plugins/USAGE.md` under Configuration Reference
3. Add a `plugins/CHANGELOG.md` entry
