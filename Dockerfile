# Dockerfile - Flask + PostgreSQL
FROM python:3.11-slim

# Direktori kerja aplikasi
WORKDIR /app

# Dependensi sistem untuk psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependensi Python
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir gunicorn

# Salin source code aplikasi
COPY . ./

# Environment runtime
ENV FLASK_APP=run.py \
    FLASK_ENV=production \
    FLASK_DEBUG=0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Port internal aplikasi
EXPOSE 5000

# Jalankan Flask melalui Gunicorn
# run.py harus memiliki objek Flask bernama app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]