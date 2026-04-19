FROM python:3.12-slim-bookworm

# System deps:
#   ghostscript/tesseract/unpaper/pngquant/qpdf — required by ocrmypdf (PDF OCR)
#   build-essential — a few Python wheels compile from source on first install
#   curl — used by Railway's healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    ghostscript \
    tesseract-ocr \
    tesseract-ocr-spa \
    unpaper \
    pngquant \
    qpdf \
    curl \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# uv is our Python package manager. Install into the system python so it's on PATH.
RUN pip install --no-cache-dir uv==0.5.11

# Install Python deps first, in a layer Docker can cache between builds. Only
# invalidates when pyproject.toml / uv.lock change — not on every source edit.
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# Then drop the source in. Source changes => rebuild from here only.
COPY backend/ /app/backend/
COPY docs/ /app/docs/

# Activate the venv created by uv sync.
ENV PATH="/app/backend/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Railway (and most PaaS) inject PORT at runtime. Fall back to 8000 for local runs.
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
