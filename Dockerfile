# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user -r requirements.txt

ENV PATH="/root/.local/bin:${PATH}"

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
ENV PATH="/root/.local/bin:${PATH}"

COPY . .

# Development target
FROM builder AS development

COPY requirements-dev.txt .
RUN pip install --user -r requirements-dev.txt

ENV PATH="/root/.local/bin:${PATH}"
ENV ENVIRONMENT=development
ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production target
FROM builder AS production

ENV ENVIRONMENT=production
ENV PYTHONPATH=/app

COPY . .

EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "python:app.core.config.gunicorn_config", "app.main:app"]
