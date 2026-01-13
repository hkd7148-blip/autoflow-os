# AUTOFLOW OS - Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim as runtime
WORKDIR /app

RUN groupadd -r autoflow && useradd -r -g autoflow autoflow
COPY --from=builder /root/.local /home/autoflow/.local
ENV PATH=/home/autoflow/.local/bin:$PATH

COPY --chown=autoflow:autoflow . .
RUN mkdir -p /app/data /app/logs && chown -R autoflow:autoflow /app

USER autoflow
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

CMD ["python", "-m", "src.bot"]
