# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies (system-wide for Docker)
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code and other files
COPY src/ src/
COPY .env.example .
COPY README.md .

# Add /app to PYTHONPATH so src.main works
ENV PYTHONPATH=/app

# Expose port 8000 for SSE
EXPOSE 8000

# Run uvicorn server (SSE mode)
CMD ["uv", "run", "uvicorn", "src.sse:app", "--host", "0.0.0.0", "--port", "8000"]
