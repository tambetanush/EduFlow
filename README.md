EduFlow (FastAPI backend + React/Vite frontend)

This repo has two projects:

- `backend/` = FastAPI + SQLAlchemy (async) + SQLite (default)
- `frontend/` = React + Vite

## Architecture Overview

This application uses a simplified, **synchronous architecture**. All AI features (reports and student explanations) are executed within the standard request-response cycle for immediate results. There are **NO dependencies** on Celery workers, Redis, or background processes. Everything runs in-process, making it extremely easy to deploy and test.

The root folder does NOT have a `package.json`, so you must run npm commands inside `frontend/`.

## Prerequisites (Windows)

- Node.js (for frontend)
- Python 3.11+ (for backend; recommended 3.11/3.12)

All commands below are written for Windows PowerShell.

1. Open PowerShell and cd into the repo
   Copy/paste (quotes are important because the path contains spaces):

```powershell
cd '<PATH TO>\EduFlow'
```

2. Backend setup (one-time)
   2.1 Create a virtual environment (if it does not exist yet)

```powershell
cd .\backend\
if (!(Test-Path .\.venv)) { python -m venv .venv }
```

2.2 Install backend dependencies (always use the venv python)

```powershell
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
```

2.3 Create backend `.env` from example (optional but recommended)

```powershell
if (!(Test-Path .\.env)) { Copy-Item .\.env.example .\.env }
```

2.4 Configure GenAI env vars in `backend\.env` (required for Admin AI Reports)

Add/update the following keys in `backend\.env`:

```env
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL_NAME=gemini-3.1-flash-lite-preview
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
AI_MAX_RETRIES=3
AI_RETRY_BASE_DELAY_SECONDS=0.5
AI_ADMIN_REPORT_CACHE_TTL_SECONDS=3600
AI_ADMIN_REPORT_PROMPT_VERSION=v1
AI_ADMIN_REPORT_USER_RATE_LIMIT=3
AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT=10
AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS=600
AI_ADMIN_REPORT_STALE_AFTER_SECONDS=900
AI_RATE_LIMIT_BACKEND=database
AI_RATE_LIMIT_COUNTER_RETENTION_SECONDS=86400

# Note: Redis/Celery are NOT required. The app is purely synchronous and DB-backed.
```

Important:

- Add API keys only in `backend\.env` (backend-only).
- Do not add Gemini keys in frontend env files.
- Keep `AI_RATE_LIMIT_BACKEND=database` for multi-instance deployments.

        2.5 Database Initialization

    The backend **automatically runs migrations** and creates the database file (`eduflow.db`) when it starts. You do not need to run manual migration commands, but you can if you wish:

```powershell
cd .\backend
.\.venv\Scripts\python -m alembic upgrade head
```

Notes:

- Default DB is SQLite: `backend\eduflow.db` (controlled by `DATABASE_URL` in `backend\.env`).
- CORS origins are controlled by `FRONTEND_ORIGINS` in `backend\.env`.

3. (Recommended) Reset DB and seed demo data
   If you previously had random/dummy data, reset the DB and load known demo data.

3.1 Stop the backend server if it is running (Ctrl+C). SQLite can stay locked while the server is running.

3.2 Delete the local SQLite DB file (safe for local dev)

```powershell
cd .\backend
if (Test-Path .\eduflow.db) { Remove-Item -Force .\eduflow.db }
```

3.3 Seed demo data (this recreates tables and inserts demo records)
IMPORTANT: use the venv python, not the system python.

```powershell
cd .\backend
.\.venv\Scripts\python -m scripts.test_data
```

4. Run the backend (FastAPI)
   Run this in one PowerShell window:

```powershell
cd .\backend
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will be at:

- http://127.0.0.1:8000

(The app will auto-create the database and run migrations on first launch)

5. Frontend setup (one-time)
   Run in a separate PowerShell window:

```powershell
cd .\frontend
npm install
```

5.1 Create frontend `.env` from example (required so the frontend knows where the backend is)

```powershell
cd .\frontend
if (!(Test-Path .\.env)) { Copy-Item .\.env.example .\.env }
```

The important frontend variable:

- `VITE_API_BASE_URL=http://localhost:8000`
  (no `/api/v1` here; the frontend appends `/api/v1` internally)

6. Run the frontend (Vite dev server)
   Run in the frontend PowerShell window:

```powershell
cd .\frontend
npm run dev
```

Frontend will be at:

- http://localhost:8080

7. Quick verification (manual)

1) Open http://localhost:8080
2) Login (try institution admin):
    - `institution.admin@eduflow.edu` / `institution123`
3) Admin portal checks:
    - Reports page should load real analytics (sampled from backend data).
    - Manage Students/Educators/Institutes should load real data (no mock lists).
    - Approvals should load real requests and approve/reject should work.
    - Salaries (admin only) should load and allow "Pay".
4) Certificate flow (institution admin):
    - Go to Certificates page and generate/issue a certificate (calls backend).

## Default seeded users

- Admin: `admin@eduflow.edu` / `admin123`
- Institution admin: `institution.admin@eduflow.edu` / `institution123`
- Educator: `educator@eduflow.edu` / `educator123`
- Student: `student@eduflow.edu` / `student123`
- Support: `support@eduflow.edu` / `support123`

## Troubleshooting

- If `npm run dev` fails at repo root: you are in the wrong folder. Run it inside `frontend/`.
- If backend errors like `No module named 'jose'`: you are using system python. Use `backend\.venv\Scripts\python`.
- If seeding fails with SQLite "database is locked": stop uvicorn (Ctrl+C) and retry seed after deleting `backend\eduflow.db`.
