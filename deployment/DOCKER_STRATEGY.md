# Docker Strategy — pdf-autofillr-plugins

The plugins package is a pure-Python library with zero runtime dependencies.
Docker is used for isolated test execution, not for serving an HTTP API.

## Image

- Base: `python:3.12-slim`
- Installs `pdf-autofillr-plugins[dev]` from the local source
- Runs `pytest plugins/tests/ -v`

## Build

```bash
# From repo root
docker build -f deployment/docker/plugins/Dockerfile -t pdf-autofillr-plugins-test:latest .
```

## Run

```bash
# Run tests in container
docker run --rm pdf-autofillr-plugins-test:latest

# Run with docker compose
docker compose -f deployment/docker/plugins/docker-compose.yml up --build
```

## CI usage

The Docker image can be used in CI to test against a clean environment:

```yaml
- run: |
    docker build -f deployment/docker/plugins/Dockerfile -t plugins-test .
    docker run --rm plugins-test
```
