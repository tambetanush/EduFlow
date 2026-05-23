from __future__ import annotations
import asyncio
import json
from fastapi.responses import Response
import yaml
import uvicorn
import os

from contextlib import asynccontextmanager
from pathlib import Path

from app.api.v1 import api_router
from app.config import settings
from app.db import engine
from app.i18n import get_locale_from_request, normalize_locale, translate_payload
from app.models import Base
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ---------------------------------------------------------------------------
# Lifespan: ensure media/ directory exists before requests start
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[type-arg]
    Path("media").mkdir(exist_ok=True)
    if settings.DATABASE_URL.startswith("sqlite+"):
        import subprocess
        import sys
        
        # Get the directory of the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(current_dir)
        
        # Run alembic upgrade head as a subprocess to avoid event loop nesting issues
        try:
            print("Checking/Running database migrations...")
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=backend_dir,
                check=True,
                capture_output=False # Let technical logs show in main terminal
            )
            print("Migrations complete.")
        except Exception as e:
            print(f"Auto-migration failed via subprocess: {e}. Attempting fallback...")
            # Fallback to create_all if alembic fails
            async with engine.begin() as connection:
                await connection.run_sync(Base.metadata.create_all)
    from app.jobs.tasks import tick_scheduled_ai_reports

    async def _scheduled_reports_loop():
        while True:
            await tick_scheduled_ai_reports()
            await asyncio.sleep(60)

    loop_task = asyncio.create_task(_scheduled_reports_loop())
    
    yield
    
    loop_task.cancel()


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def locale_middleware(request: Request, call_next):
    request.state.locale = normalize_locale(
        request.headers.get("x-language") or request.headers.get("accept-language")
    )
    response = await call_next(request)
    response.headers["Content-Language"] = request.state.locale

    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return response

    body = b""
    async for chunk in response.body_iterator:
        body += chunk

    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception:
        return Response(
            content=body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type,
        )

    translated = translate_payload(payload, get_locale_from_request(request))
    headers = dict(response.headers)
    headers.pop("content-length", None)
    return JSONResponse(
        content=translated,
        status_code=response.status_code,
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    locale = get_locale_from_request(request)
    translated_errors = []
    for error in exc.errors():
        item = dict(error)
        if isinstance(item.get("msg"), str):
            item["msg"] = translate_payload(item["msg"], locale, "msg")
        translated_errors.append(item)
    return JSONResponse(status_code=422, content={"detail": translated_errors})

# ---------------------------------------------------------------------------
# Static file serving for uploads  (mounted after media/ is guaranteed)
# ---------------------------------------------------------------------------

# also create at import time for hot-reload
Path("media").mkdir(exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# ---------------------------------------------------------------------------
# API routers — all under /api/v1
# ---------------------------------------------------------------------------

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/", tags=["health"])
async def health() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/openapi.yaml", response_class=Response, include_in_schema=False)
def get_openapi_yaml():
    openapi_spec = app.openapi()  # Generates the spec as a Python dict (JSON compatible)
    # Converts dict to YAML string
    openapi_yaml = yaml.dump(openapi_spec, default_flow_style=False)
    return Response(content=openapi_yaml, media_type="application/x-yaml")
