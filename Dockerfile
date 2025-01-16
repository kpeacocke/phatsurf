# Stage 1: Builder
FROM python:3.13-slim AS builder

# Install system dependencies and Poetry
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    curl=7.88.1-10+deb12u8 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && curl --fail --proto '=https' --tlsv1.2 -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Copy the project files
COPY pyproject.toml poetry.lock ./

# Install dependencies in a virtual environment
RUN poetry config virtualenvs.create false && poetry install --no-root --only main

# Copy the rest of the application files
COPY /app /app
COPY /run.py /run.py

# Stage 2: Final runtime image
FROM python:3.13-slim

# Create a non-root user
RUN groupadd -r surfDude && useradd -r -g surfDude surfDude

# Set the working directory
WORKDIR /app

# Copy installed dependencies and application code from the builder
COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /app /app
COPY --from=builder /run.py /run.py

# Change ownership to the non-root user
RUN chown -R surfDude:surfDude /app

# Switch to the non-root user
USER surfDude

# Expose the Flask port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0  
ENV FLASK_RUN_PORT=5000
ENV PYTHONUNBUFFERED=1 
ENV PYTHONPATH="/app" 

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", \
    "import http.client as httplib; conn = httplib.HTTPConnection('localhost', \
    5000); conn.request('GET', '/health'); exit(0) if conn.getresponse().status \
    == 200 else exit(1)"]

# Add metadata labels
LABEL maintainer="Kristian Peacocke <krpeacocke@gmail.com>"
LABEL version="1.0"
LABEL description="PhatSurf Flask Application"

# Command to run the application
CMD ["python", "../run.py"]