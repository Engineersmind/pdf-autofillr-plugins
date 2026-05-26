FROM python:3.12-slim

WORKDIR /app

# Copy the plugins package
COPY plugins /app/plugins

# Install with dev extras
RUN pip install --no-cache-dir -e "plugins[dev]"

# Default command: run the full test suite
CMD ["pytest", "plugins/tests/", "-v", "--tb=short"]
