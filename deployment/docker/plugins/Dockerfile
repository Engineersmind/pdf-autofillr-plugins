FROM python:3.12-slim
WORKDIR /app
COPY packages/plugins /app/packages/plugins
RUN pip install --no-cache-dir -e "packages/plugins[dev]"
CMD ["pytest", "packages/plugins/tests/", "-v"]
