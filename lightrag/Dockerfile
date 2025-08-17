# LightRAG Service Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app/lightrag_service

# Create necessary directories
RUN mkdir -p /app/data /app/config /app/logs

# Set environment variables
ENV PYTHONPATH=/app:$PYTHONPATH \
    PYTHONUNBUFFERED=1 \
    LIGHTRAG_WORKING_DIR=/app/data

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose API port
EXPOSE 8080

# Run the application
CMD ["python", "/app/lightrag_service/simple_api.py"]