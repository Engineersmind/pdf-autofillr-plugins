# pdf-autofillr-plugins — Deployment Plan

## PyPI (primary distribution)

```bash
# 1. Bump version in plugins/pyproject.toml and __init__.py
# 2. Update plugins/CHANGELOG.md and root CHANGELOG.md
# 3. Merge to main via PR
# 4. Push tag — CI does the rest

git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
```

Tags matching `plugins-v*` trigger the CI publish workflow automatically using
PyPI Trusted Publishing (OIDC) — no API token required.

## Docker (testing only)

The Docker image is used to verify plugin loading and test execution in isolation.
It does not serve any HTTP API — plugins are a library, not a server.

```bash
# From repo root
docker compose -f deployment/docker/plugins/docker-compose.yml up --build
```

## Local development install

```bash
cd plugins
pip install -e ".[dev]"
pytest tests/ -v
```

## Release CI flow

```
git tag plugins-v0.2.0
        ↓
tests.yml: Python 3.10 / 3.11 / 3.12
        ↓
publish-pypi.yml:
  test → verify version matches tag → build wheel+sdist → publish via OIDC
        ↓
update-changelog.yml:
  extract entry from plugins/CHANGELOG.md → prepend to root CHANGELOG.md → commit to main
```
