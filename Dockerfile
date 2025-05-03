FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_DEBUG=0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn gevent

# Create necessary directories
RUN mkdir -p /app/logs

# Copy application code
COPY . .

# Run database migrations if using SQLite (not needed for PostgreSQL)
RUN python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Set up a non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Start gunicorn
CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"] 