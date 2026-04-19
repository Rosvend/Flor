# Flor — PQRSmart

PQRSD optimization system for the Alcaldía de Medellín (Secretaría de Desarrollo
Económico). Submission for **OmegaHack 2026** — track *AI Agents & Automation*.

Flor automates the non-discretionary parts of the PQRSD workflow (ingestion,
pre-classification, synthesis, RAG-based draft responses) so officials spend
their 15-business-day legal budget on legal review, not on routing and reading.

See [`CLAUDE.md`](CLAUDE.md) for architecture, components (A/B/C), and the legal
framework the MVP operates under. See [`DEPLOY.md`](DEPLOY.md) for the live
Railway + Vercel deployment guide.

---

## Repository layout

```
Flor/
├── backend/        # FastAPI + Clean Architecture (src/domain, application, interfaces, infrastructure)
├── frontend/       # Vite (vanilla JS) — citizen UI + functionary console + admin KB panel
├── docs/           # PDFs and markdown sources for the knowledge base
├── docker-compose.yml   # Postgres 16 on :5433 (seeds schema from backend/migrations)
├── Dockerfile      # Production image (used by Railway)
├── CLAUDE.md       # Architecture + domain rules (authoritative spec)
└── DEPLOY.md       # Railway + Vercel deployment
```

---

## Prerequisites

Evaluators will need the following installed on the host machine:

| Tool | Why | Install |
|---|---|---|
| **Python 3.12** | Backend runtime (pinned via `backend/.python-version`) | `uv` will fetch this automatically |
| **[`uv`](https://docs.astral.sh/uv/)** | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **Docker + Docker Compose** | Local Postgres 16 | [get.docker.com](https://get.docker.com) |
| **Node.js ≥ 18** | Vite dev server for the frontend | [nodejs.org](https://nodejs.org) |
| **Tesseract OCR (Spanish pack)** | OCR step in the knowledge-base PDF pipeline | `sudo apt install tesseract-ocr tesseract-ocr-spa ghostscript unpaper pngquant qpdf` |

You will also need **external API credentials** for the full experience:

- **Google Gemini API key** — required for classification, summarization, draft
  responses and the Flor chatbot. Free tier works for the demo
  (`gemini-2.5-flash-lite`). Create one at <https://aistudio.google.com/app/apikey>.
- **AWS S3 bucket + IAM credentials** — raw and curated PQRSDs are persisted in
  S3 (the data lake). Any bucket in `us-east-1` with `s3:GetObject/PutObject/ListBucket`
  is enough.
- *(Optional)* **Gmail app password** — enables the IMAP ingestion scheduler
  (`EMAIL_INGEST_*`) that pulls PQRSDs from an inbox.
- *(Optional)* **Meta Page Access Token** — enables Facebook DM ingestion.

If you don't have S3 credentials, the app still boots: ingestion endpoints will
return errors but the login, dashboard, summaries and chatbot work.

---

## Quick start — local

Run these from the repo root unless stated otherwise. Commands are idempotent;
you can re-run any of them.

### 1. Start Postgres

```bash
docker compose up -d
```

Postgres listens on **localhost:5433** (not 5432 — chosen to avoid conflicts
with a local install). The schema in `backend/migrations/001_create_users.sql`
is applied automatically on first boot.

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and fill in at minimum:

```ini
# DB (already correct for the docker-compose service)
DATABASE_URL=postgresql://flor:flor@localhost:5433/flor

# Auth
JWT_SECRET=<32+ random chars — generate with: openssl rand -hex 32>
JWT_EXPIRE_MINUTES=60

# AI (required for classification / summary / chatbot)
GEMINI_API_KEY=<your key>
GEMINI_MODEL=gemini-2.5-flash-lite

# S3 data lake (required for ingestion + curated endpoints)
S3_RAW_BUCKET=<your-bucket>
S3_RAW_PREFIX=raw/
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<…>
AWS_SECRET_ACCESS_KEY=<…>

# Frontend origins allowed by CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Optional blocks (Meta ingestion, IMAP, SMTP) are documented inline in
`backend/.env.example`. Leave them at their placeholders if unused.

### 3. Install Python dependencies

```bash
cd backend
uv sync
```

`uv sync` reads `pyproject.toml` + `uv.lock`, creates `backend/.venv/`, and
installs everything in one shot. First run downloads torch/transformers/chromadb
(~2–3 GB), subsequent runs are instant.

### 4. Build the knowledge base (Chroma index)

Converts the PDFs in `docs/` to markdown, chunks semantically, and indexes them
into a local Chroma store at `backend/.knowledge_base/chroma/`. This is what
powers Flor's RAG (draft responses + chatbot).

```bash
# from backend/
uv run python -m src.interfaces.cli.build_knowledge_base --rebuild
```

First run also downloads the sentence-transformers embedding model (~400 MB).
Useful flags: `--only <pdf>`, `--dry-run`, `--force-reconvert`, `-v`.

### 5. Seed the database

```bash
# from backend/
uv run python -m scripts.seed_departments   # 30 Alcaldía departments / subsecretarías
uv run python -m scripts.seed_users         # 15 functionary users (password: Flor2026!)
uv run python scripts/seed_admin.py         # admin@flor.com / admin123
```

### 6. Run the backend

```bash
# from backend/
uv run uvicorn main:app --reload
```

The API binds to <http://127.0.0.1:8000>. Smoke-test it:

```bash
curl http://127.0.0.1:8000/health
# → {"status":"ok","service":"pqrs-backend"}
```

FastAPI's auto-generated Swagger UI is served at
<http://127.0.0.1:8000/docs>.

### 7. (Optional) Seed sample PQRSDs into S3

Populates the dashboard with realistic curated PQRSDs across multiple
departments. Requires valid S3 credentials **and** the backend running.

```bash
# from backend/
uv run python -m scripts.seed_curated_v2 --url http://localhost:8000
```

`seed_curated_v2` wipes the `curated/` prefix in S3 first and then uploads 20
PQRSDs (10 for Desarrollo Económico + 10 spread across random departments).
For a lighter 5-record sample use `scripts.seed_curated_pqrsds` instead.

### 8. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server binds to <http://localhost:5173>. The client picks up the
backend URL from `VITE_API_BASE_URL` and falls back to
`http://127.0.0.1:8000/api/v1` for local dev — no extra config needed.

---

## How to log in (demo accounts)

| Role | Email | Password |
|---|---|---|
| Admin (knowledge-base uploads, everything) | `admin@flor.com` | `admin123` |
| Functionary – Desarrollo Económico | `funcionario1.desarrolloeconomico@medellin.gov.co` | `Flor2026!` |
| Functionary – other departments | `funcionario.<label>@medellin.gov.co` (see console output of `seed_users.py`) | `Flor2026!` |

---

## What to look at during the demo

- **Home** (`/`) — citizen-facing landing with the Flor chatbot floating
  widget. Ask *"cómo radico una PQR"* to exercise the RAG pipeline.
- **Citizen submission** (`/pqrs`) — the form a ciudadano uses to file a PQRSD.
  Submissions go through the curated ingestion endpoint into S3.
- **Status lookup** (`/pqrs-status`) — track a filing by radicado.
- **Login** (`/login`) — authenticate as a functionary or admin.
- **Functionary console** (`/aplicacion`) — the bandeja. Left sidebar lists
  PQRSDs for your organization. Open one and use:
  - **Generar resumen** → produces the 3-layer synthesis (Component C).
  - **Generar borrador** → produces a Spanish draft response with cited sources
    via RAG over the knowledge base + precedents.
  - **Reclasificar** → corrects the suggested department and persists the fix
    back to S3.
- **Admin KB** (`/admin/knowledge-base`) — upload new PDFs at runtime; the
  server chunks and indexes them into the live Chroma collection.

---

## Running the tests

```bash
# from backend/
uv run pytest
```

Domain and application layers have unit tests. Infrastructure tests under
`tests/integration/` expect a reachable Postgres (the docker-compose one is
enough).

---

## Deployment

Full production deployment targeting **Railway (backend) + Vercel (frontend)**
with Postgres plugin and a persistent Chroma volume is documented in
[`DEPLOY.md`](DEPLOY.md).

---

## Troubleshooting

- **`docker compose up` fails with "port 5433 already in use"** — another
  Postgres is on that port. Edit `docker-compose.yml` to map a different host
  port and update `DATABASE_URL` accordingly.
- **`ocrmypdf` complains about `ghostscript`/`unpaper`** — install the system
  packages in the prerequisites table. The KB build falls back to PDF-native
  text extraction when OCR isn't needed, so this only matters for scanned PDFs.
- **KB build warns "No PDFs found"** — check that `docs/*.pdf` exists. The two
  source documents (`Manual_buenas_practicas.pdf`, `secretarias.pdf`) are
  tracked in the repo.
- **`401 Unauthorized` after logging in** — your `JWT_SECRET` changed while a
  token was still valid in the browser. Log out and back in.
- **Gemini `429` errors** — free-tier daily quota hit. Switch
  `GEMINI_MODEL` to another free model (`gemini-2.5-flash`,
  `gemini-2.5-flash-lite`) or add billing.
- **Backend falls back to in-memory user repo** — the startup log prints
  *"Cayendo en modo IN-MEMORY"*. This means `DATABASE_URL` is unset or Postgres
  is unreachable. Fix the env var, re-run `docker compose up -d`, and restart
  the server.

---

## License and attribution

Built for OmegaHack 2026 at Universidad EAFIT, Medellín.
