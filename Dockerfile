# ==========================================
# Dockerfile - Flask + PostgreSQL (Production)
# ==========================================
FROM python:3.11-slim

# Direktori kerja aplikasi
WORKDIR /app

# Dependensi sistem untuk psycopg2 dan compiler
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependensi Python (Salin requirements.txt terlebih dahulu)
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && python -m pip install --no-cache-dir gunicorn

# Salin seluruh source code aplikasi ke dalam container
COPY . ./

# Environment runtime (FLASK_ENV dihapus karena deprecated di Flask modern)
ENV FLASK_APP=run.py \
    FLASK_DEBUG=0 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Port internal aplikasi
EXPOSE 5000

# Jalankan Flask melalui Gunicorn
# Pastikan file run.py memiliki instance aplikasi Flask bernama 'app'
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]