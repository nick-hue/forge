FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY api/ api/

COPY worker/ worker/

FROM python:3.12-slim

WORKDIR /app

RUN useradd --create-home --system appuser

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/api /app/api
COPY --from=builder /app/worker /app/worker

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]




