# Docker Strategy — pdf-autofillr-plugins

The plugins image is used to test plugin loading and execution in isolation.

## Image
- Base: `python:3.12-slim`
- Installs `pdf-autofillr-plugins[dev]`
- Runs `pytest tests/ -v`
