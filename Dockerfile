# Stage 1: Base image for both dev and prod
FROM python:3.13-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy application source files
COPY pyproject.toml poetry.lock ./
COPY app/ ./app
COPY run.py .

# Install system dependencies and Poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    curl=7.88.1-10+deb12u8 && \
    curl --fail --proto '=https' --tlsv1.2 -sSL https://install.python-poetry.org | python3 - && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Stage 2: Development dependencies
FROM base AS development_base
RUN poetry config virtualenvs.create false && poetry install --with dev --no-root && \
    poetry add debugpy --group dev

# Stage 3: Production dependencies
FROM base AS production_base
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Stage 4a: Development image
# Final runtime image
FROM python:3.13-slim AS development

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Default to development dependencies
COPY --from=development_base /root/.local /root/.local
COPY --from=development_base /usr/local/lib/python3.13 /usr/local/lib/python3.13

# Create a non-root user
RUN groupadd -r surfDude && useradd -r -g surfDude surfDude

# Switch to the non-root user
USER surfDude

# Expose the Flask port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", \
    "import http.client as httplib; conn = httplib.HTTPConnection('localhost', \
    5001); conn.request('GET', '/health'); exit(0) if conn.getresponse().status \
    == 200 else exit(1)"]

# Stage 4b: Final runtime image
FROM python:3.13-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Default to production dependencies
COPY --from=production_base /root/.local /root/.local
COPY --from=production_base /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=production_base /app /app

# Create a non-root user
RUN groupadd -r surfDude && useradd -r -g surfDude surfDude

# Switch to the non-root user
USER surfDude

# Expose the Flask port
EXPOSE 5001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", \
    "import http.client as httplib; conn = httplib.HTTPConnection('localhost', \
    5001); conn.request('GET', '/health'); exit(0) if conn.getresponse().status \
    == 200 else exit(1)"]

# Command for Gunicorn
CMD ["python3", "-m", "gunicorn", "-b", "0.0.0.0:5001", "--workers", "4", "--threads", "2", "app:create_app()"]