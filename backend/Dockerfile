# Use Python 3.13 slim image
FROM python:3.13-slim

# Install build dependencies and uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "app/main.py"]
