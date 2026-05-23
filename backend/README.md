# EduFlow Backend

FastAPI + SQLAlchemy async backend for the EduFlow full-stack application.

Local development now defaults to SQLite. PostgreSQL can still be used later by changing `DATABASE_URL`.

## Architecture (Synchronous & Simple)

This application uses a purely **synchronous architecture**. AI report generation and student explanations are performed inline within the request-response cycle. 

There is **NO** dependency on a Celery worker, Celery Beat, or Redis. This drastically simplifies local development and deployments.

## Development

1. Create `backend/.env` from `backend/.env.example`.
2. Install dependencies:

```sh
pip install -e ".[dev]"
```

3. Run migrations:

```sh
python -m alembic upgrade head
```

For the default SQLite setup, the app and seed script will also auto-create tables on first run. Alembic can still be used later when you formalize migrations.

4. Seed baseline users:

```sh
python -m scripts.test_data
```

For a full local demo dataset across all core tables, use:

```sh
python -m scripts.test_data
```

This resets the SQLite database, recreates the schema, and loads linked demo data for institutions, users, workshops, modules, enrollments, sessions, attendance, assessments, questions, submissions, certificates, fees, payments, and notifications.

5. Start the API:

```sh
uvicorn app.main:app --reload
```

OR

```sh
python -m uvicorn app.main:app --reload
```

This will create `backend/eduflow.db` locally when using the default SQLite configuration. The background scheduled loop for AI reports will start automatically on application launch.

## GenAI setup (Admin AI Reports)

GenAI configuration is backend-only. Add your Gemini key in `backend/.env`.

Required env vars:

```env
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL_NAME=gemini-3.1-flash-lite-preview
GEMINI_API_BASE_URL=https://generativelanguage.googleapis.com
GEMINI_TIMEOUT_SECONDS=30
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

# Redis/Celery are NOT required. The app is purely synchronous and DB-backed.
```

Production notes:

- Keep `GEMINI_MODEL_NAME` on a stable version (`gemini-3.1-flash-lite-preview`).
- Keep `AI_RATE_LIMIT_BACKEND=database` for multi-instance-safe limits.
- `AI_RATE_LIMIT_BACKEND=memory` is only for local/single-process dev.
- Do not put Gemini keys in frontend env files.

After updating `.env`, run:

```sh
python -m alembic upgrade head
```

This creates/updates AI tables used by admin report generation and DB-backed rate limiting.

## Database options

- Default local DB: `sqlite+aiosqlite:///./eduflow.db`
- Optional later upgrade: set `DATABASE_URL` to a PostgreSQL URL such as `postgresql+asyncpg://postgres:postgres@localhost:5432/eduflow`

## Default seeded users

- Admin: `admin@eduflow.edu` / `admin123`
- Institution admin: `institution.admin@eduflow.edu` / `institution123`
- Educator: `educator@eduflow.edu` / `educator123`
- Student: `student@eduflow.edu` / `student123`
- Technical support: `support@eduflow.edu` / `support123`

## Frontend integration

- API prefix: `/api/v1`
- Auth flow:
    - `POST /api/v1/auth/login`
    - `GET /api/v1/users/me`
    - `POST /api/v1/auth/refresh`
- Minimal password reset support:
    - `POST /api/v1/auth/forgot-password`
    - `POST /api/v1/auth/reset-password`

CORS is controlled by `FRONTEND_ORIGINS`, which should match the Vite dev origin(s).

## Dashboard endpoints

Used by the frontend dashboards:

- GET /api/v1/dashboard/admin (admin)
- GET /api/v1/dashboard/student/{student_id} (student self)
- GET /api/v1/dashboard/educator (staff)

## Certificates

- GET /api/v1/certificates/ (staff list)
- GET /api/v1/certificates/student/{student_id}
- GET /api/v1/certificates/verify/{verification_code} (public)
