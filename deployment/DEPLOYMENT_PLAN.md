# pdf-autofillr-plugins — Deployment Plan

## PyPI release

```bash
make build && make publish
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
```

Tags matching `plugins-v*` trigger the CI publish workflow automatically.
