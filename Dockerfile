# Base image
FROM python:3.11-slim

# Environment variables for Python & pip
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Install system dependencies (PDF parsing, HTML, build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential curl \
       poppler-utils libxml2 libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create non-root user for security
RUN useradd --create-home appuser
USER appuser

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./README.md ./README.md

# Expose port for ECS / ALB
EXPOSE 8080

# Health check for ECS/ALB
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Command to run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]