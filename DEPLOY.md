# Deployment — Railway (backend) + Vercel (frontend)

Target: a live URL by demo day. The backend is a Python + FastAPI image
(~3 GB because of torch/transformers/chromadb); Vercel's serverless cap is
250 MB, so the backend must live somewhere else. Railway handles it in one
shot with a managed Postgres plugin and a persistent volume.

## Prerequisites

- Railway account + CLI optional (we use the web dashboard).
- Vercel project already exists with the frontend deployed.
- A Gemini API key with room in one of the Gemini 2.5 models.
- The AWS S3 bucket and IAM creds already in use locally.

## Architecture after deploy

```
Browser ──► Vercel (static Vite build)                ──► GitHub
                │
                │ fetch(VITE_API_BASE_URL)
                ▼
             Railway
             ├── web: this repo (Dockerfile at root)   ──► /health
             ├── Postgres plugin (DATABASE_URL)
             └── Volume /app/backend/.knowledge_base (Chroma persisted)
                        │
                        ├── Gemini API
                        └── S3 bucket (curated data lake)
```

## Railway — one-time setup

1. **New Project → Deploy from GitHub repo** → pick this repo, branch `main`.
2. Railway detects the `Dockerfile` at the repo root and starts the first build.
   This takes 8–12 min the first time (torch + transformers are large). Subsequent
   builds reuse layers and take ~2 min.
3. **Add a Postgres plugin**: project → `+ New` → Database → Postgres. Railway
   injects `DATABASE_URL` into the web service automatically.
4. **Add a Volume** to the web service: Settings → Volumes → `+ New Volume`.
   Mount path: `/app/backend/.knowledge_base`. Size: 5 GB is plenty.
5. **Set environment variables** (Service → Variables):

   | Variable | Value | Notes |
   |---|---|---|
   | `GEMINI_API_KEY` | `AIza…` | paste from local `.env` |
   | `GEMINI_MODEL` | `gemini-2.5-flash-lite` | swap if quota dies |
   | `JWT_SECRET` | 32+ random chars | **do not** reuse local value in prod |
   | `JWT_EXPIRE_MINUTES` | `60` | optional |
   | `CORS_ORIGINS` | `https://<your-app>.vercel.app,https://flor.vercel.app` | comma-separated |
   | `S3_RAW_BUCKET` | `pqrsd-datalake` | same as local |
   | `S3_RAW_PREFIX` | `raw/` | |
   | `S3_CURATED_PREFIX` | `curated/` | optional |
   | `AWS_REGION` | `us-east-1` | |
   | `AWS_ACCESS_KEY_ID` | `AKIA…` | same as local |
   | `AWS_SECRET_ACCESS_KEY` | `…` | |
   | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` | — | only if email notifications are wanted |
   | `CHATBOT_FALLBACK_MESSAGE`, `CHATBOT_TOP_K`, `CHATBOT_MIN_SIMILARITY` | defaults are fine | |

   `DATABASE_URL` is already there from the Postgres plugin — do not paste a local value.

6. **Redeploy**. Wait for green status. Open the generated domain (Settings → Networking →
   Generate Domain) and hit `/health` — expect `{"status":"ok","service":"pqrs-backend"}`.

## Bootstrap the database and the Chroma index

Railway exposes a shell via **Service → Shell** (or `railway run bash` via CLI). Run
these, in order, from the shell:

```bash
# 1. User/department schema + seed data
python scripts/seed_departments.py   # 30 departments with org_id
python scripts/seed_users.py         # 15 functionary users (Flor2026!)
python scripts/seed_admin.py         # admin@flor.com / admin123

# 2. (Optional) seed sample curated PQRs into S3 so the dashboard isn't empty
python -m scripts.seed_curated_pqrsds --url http://localhost:${PORT}

# 3. Build the knowledge-base index into the persistent volume (~3–4 min)
python -m src.interfaces.cli.build_knowledge_base --rebuild --verbose
```

Hit `/api/v1/auth/login` with `admin@flor.com`/`admin123` to confirm everything's wired.

## Vercel — point the frontend at Railway

1. Project → Settings → Environment Variables → add `VITE_API_BASE_URL` with value
   `https://<your-railway-app>.up.railway.app/api/v1` for Production (and Preview
   if you want).
2. Redeploy the frontend from the Vercel dashboard (or push a no-op commit).

The frontend code already honors `VITE_API_BASE_URL` (`frontend/src/service/api.js:4`),
falling back to `http://127.0.0.1:8000/api/v1` in local dev.

## Smoke-test checklist (do before the demo)

- `curl https://<railway>/health` → 200 `{"status":"ok"}`.
- Vercel site loads, navbar visible, no console errors about BASE_URL.
- Log in with `admin@flor.com` / `admin123`.
- `/aplicacion` loads the bandeja (left sidebar shows seeded PQRs).
- Open a PQR → **Generar resumen** returns a lead+topics card; **Generar borrador**
  returns a formal Spanish draft with sources.
- `/admin/knowledge-base` → upload a small PDF → toast says "Indexados N fragmentos".
- Home page → click Flor → ask "cómo radico una PQR" → conversational reply.

## Cost + quota watch-outs

- Railway: first $5/mo of usage is free. The torch-based image + a small
  Postgres + a persistent volume = ~$10/mo steady-state if left on 24/7. Pause
  the service after the demo to stop the meter.
- Gemini free tier: 20 requests/day total across all free models. Switch
  `GEMINI_MODEL` between `gemini-2.5-flash-lite`, `gemini-2.5-flash`, etc. if
  one model's daily budget blows during the demo. For safety, upgrade the
  Gemini key to the paid tier — cost is negligible at demo volumes.
- AWS S3: calls charge per request, cache in the `S3CuratedDataLake` is 60s.
  Not a concern at demo load.

## Fast rollback

If a deploy breaks production, Railway keeps the previous deployment warm —
Service → Deployments → `…` → Redeploy on the last green build. No data loss
because Postgres and the Chroma volume are decoupled from the image.
