# ============================================================
# Dockerfile — Flask + PostgreSQL
# ============================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (untuk psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh project
COPY . .

# Environment
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Port Flask
EXPOSE 5000

# Gunicorn untuk production (WSGI)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]