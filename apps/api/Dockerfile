FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY apps/api ./apps/api
COPY packages/connectors ./packages/connectors
COPY infrastructure/migrations ./infrastructure/migrations
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "neurogenesis_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
