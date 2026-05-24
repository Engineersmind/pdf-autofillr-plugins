> **Dependabot PR?** Skip the checklist — verify CI is green, review the diff, then merge.

---

## Description
<!-- What does this PR do? Be specific. -->

## Why
<!-- Why is this change needed? Link to an issue if applicable. -->
Closes #

## Changes Made
<!-- List the key changes -->
-
-

## Testing
<!-- How did you test this? What commands did you run? -->
```bash

```

## Screenshots (if applicable)

---

## Checklist

**Branch & commits**
- [ ] Branch named correctly — `<type>/<module>-<short-description>` (e.g. `feature/plugins-phone-validator`)
- [ ] All commit messages follow `<type>/<module>: description` (e.g. `feature/plugins: add phone validator`)
- [ ] PR title follows the same format
- [ ] No direct commits to `main`

**Code**
- [ ] `pip install -e ".[dev]"` succeeds
- [ ] `pytest tests/` passes locally
- [ ] New plugins have unit AND integration tests
- [ ] New built-ins exported from `builtin/<category>/__init__.py`
- [ ] No build artifacts, `.env`, `__pycache__`, or `.egg-info` included

**Docs**
- [ ] `plugins/CHANGELOG.md` entry added
- [ ] `plugins/USAGE.md` updated if new plugin or interface added
- [ ] Root `README.md` updated if new built-in plugin added
