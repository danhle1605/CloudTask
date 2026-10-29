# Dockerfile for CloudTask (Python Flask on Gunicorn)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Install system dependencies (libpq for postgresql connectivity)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose web server port (default 5000, Render will assign $PORT dynamically)
ENV PORT=5000
EXPOSE 5000

# Health check using the readiness probe
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-5000}/health/ready || exit 1

# Run with Gunicorn bound to $PORT (Twelve-Factor stdout logging)
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 3 --access-logfile - --error-logfile - wsgi:app"]
