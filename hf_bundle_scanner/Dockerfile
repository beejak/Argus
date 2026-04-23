# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PROMPTFOO_DISABLE_TELEMETRY=1 \
    NO_ANALYTICS=1

WORKDIR /opt/llm-scanner

COPY model-admission /opt/llm-scanner/model-admission
COPY hf_bundle_scanner /opt/llm-scanner/hf_bundle_scanner

RUN pip install --upgrade pip \
    && pip install -e "/opt/llm-scanner/model-admission" \
    && pip install -e "/opt/llm-scanner/hf_bundle_scanner[http,mcp]"

ENV HF_BUNDLE_ADMIT_CMD="admit-model"

ENTRYPOINT ["scan-bundle"]
CMD ["manifest", "--help"]
