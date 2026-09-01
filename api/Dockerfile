# Build from repo root:
#   docker build -f api/Dockerfile -t ai-lab-api .
# Run locally:
#   docker run --env-file .env -p 8080:8080 ai-lab-api

FROM python:3.12-slim

WORKDIR /app

# Chroma / some wheels need basic build tooling on slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt api/requirements-demos.txt api/
RUN pip install --no-cache-dir \
    -r api/requirements.txt \
    -r api/requirements-demos.txt

COPY . .

ENV PYTHONUNBUFFERED=1 \
    LLM_PROVIDER=groq \
    WHISPER_MODEL=openai/whisper-tiny.en

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health')"

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
