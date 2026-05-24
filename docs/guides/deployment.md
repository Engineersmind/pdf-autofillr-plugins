# Deployment — pdf-autofillr-plugins

## PyPI

See [PYPI_RELEASE.md](../../PYPI_RELEASE.md) for full release instructions.

```bash
git tag plugins-v0.2.0 && git push origin plugins-v0.2.0
# CI handles build + publish automatically via OIDC Trusted Publishing
```

## Docker (test environment)

```bash
# Build
docker build -f deployment/docker/plugins/Dockerfile -t pdf-autofillr-plugins-test .

# Run tests
docker run --rm pdf-autofillr-plugins-test

# Compose
docker compose -f deployment/docker/plugins/docker-compose.yml up --build
```

## Using plugins in other packages

Once installed, plugins are imported by class name — no server or port needed:

```python
from pdf_autofillr_plugins import PluginManager
manager = PluginManager(plugin_paths=["./my_plugins/"])
```

To use plugins with the CLI:

```bash
pdf-autofillr-cli plugins list --path ./my_plugins/
pdf-autofillr-cli plugins info phone-validator
```
