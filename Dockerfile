FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production \
    SUPABASE_STORAGE_BUCKET=ATSDocumentos \
    PORT=10000

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    unzip \
    fontconfig \
    fonts-dejavu-core \
    fonts-liberation \
    fonts-noto-core \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["sh", "-c", "if [ -z \"${DATABASE_URL}\" ]; then echo \"ERROR: DATABASE_URL is required in container runtime to avoid SQLite fallback.\" >&2; exit 1; fi; python -m reflex run --env prod --single-port --backend-host 0.0.0.0 --backend-port ${PORT:-10000}"]
