FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir . \
    && useradd --create-home --uid 1000 mcp
USER mcp

# Talks MCP over stdio - no port to expose.
ENTRYPOINT ["python", "-m", "tandoor_mcp"]
