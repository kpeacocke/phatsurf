# Use an official Python runtime as the base image
FROM python:3.13-slim AS builder

LABEL maintainer="krpeacocke@gmail.com"
LABEL version="0.1"
LABEL description="PhatSurf Flask application"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Environment variables (default values can be overridden at runtime)
ENV FLASK_ENV=production
ENV MONGO_URI=mongodb://localhost:27017/phatsurf

# Set the working directory
WORKDIR /app

# Copy application source files
COPY run.py .
COPY app/ ./app
COPY pyproject.toml poetry.lock ./

# Install Poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends curl=7.88.1-10+deb12u8 && \
    curl -sSL --proto '=https' --tlsv1.2 https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && apt-get autoremove -y && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Install dependencies in a virtual environment
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Final stage: Slim runtime image
FROM python:3.13-slim

# Create a non-root user
RUN groupadd -r surfDude && useradd -r -g surfDude surfDude

# Set the working directory
WORKDIR /app

# Copy installed dependencies from the builder
COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /app /app

# Change ownership to the non-root user
RUN chown -R surfDude:surfDude /app

# Switch to the non-root user
USER surfDude

# Expose the Flask port
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD ["python", "-c", "import requests; exit(0) if requests.get('http://localhost:5000/health').status_code == 200 else exit(1)"]

# Command to run the application
CMD ["python", "run.py"]