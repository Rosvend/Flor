# Flor

PQRSD optimization system for Alcaldía de Medellín. OmegaHack 2026 — Secretaría de Desarrollo Económico.

See [`CLAUDE.md`](CLAUDE.md) for architecture, legal constraints, and component scope.

## Getting Started

### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (package + Python manager)
- `tesseract-ocr` with Spanish language pack (required for OCR'd PDFs during KB ingest):
  ```
  sudo apt install tesseract-ocr tesseract-ocr-spa ghostscript
  ```

### Install

```
cd backend
uv sync
```

`uv` reads `pyproject.toml` + `uv.lock` and creates a managed `.venv/`. Python 3.12 is pinned in `backend/.python-version`.

### Build the knowledge base

Converts PDFs in `docs/` to markdown, chunks semantically, and indexes into Chroma at `backend/.knowledge_base/chroma/`.

```
cd backend
uv run python -m src.interfaces.cli.build_knowledge_base --rebuild
```

Useful flags: `--only <pdf>`, `--dry-run`, `--force-reconvert`, `-v`.

### Run the API

```
cd backend
uv run uvicorn main:app --reload
```

### Run tests

```
cd backend
uv run pytest
```
