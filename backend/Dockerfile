FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache /tmp/*

# Copy application code
COPY . .

# Create keys directory with proper permissions
RUN mkdir -p /app/keys && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Do NOT hardcode EXPOSE — Render injects $PORT at runtime
# Use start.py entrypoint so uvicorn logs go to stdout (not stderr)
CMD ["python", "start.py"]
