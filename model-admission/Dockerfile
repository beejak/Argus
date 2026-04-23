# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PROMPTFOO_DISABLE_TELEMETRY=1 \
    NO_ANALYTICS=1

WORKDIR /opt/model-admission

COPY requirements-worker.txt pyproject.toml README.md ./
COPY model_admission ./model_admission/

RUN pip install --upgrade pip \
    && pip install -r requirements-worker.txt \
    && pip install .

ENTRYPOINT ["admit-model"]
CMD ["scan", "--help"]
