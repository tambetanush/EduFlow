from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

def _create_engine():
    engine_kwargs: dict[str, object] = {
        "echo": settings.DEBUG,
    }

    if settings.DATABASE_URL.startswith("sqlite+"):
        engine_kwargs["connect_args"] = {
            "check_same_thread": False,
            "timeout": 20,  # Increase busy_timeout to 20 seconds
        }
    else:
        engine_kwargs["pool_pre_ping"] = True
        engine_kwargs["pool_size"] = 10
        engine_kwargs["max_overflow"] = 20

    return create_async_engine(settings.DATABASE_URL, **engine_kwargs)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
engine = _create_engine()

# Enable WAL mode for SQLite to improve concurrency
if settings.DATABASE_URL.startswith("sqlite+"):
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# ---------------------------------------------------------------------------
# Session factory
# ---------------------------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


# ---------------------------------------------------------------------------
# Dependency – use as FastAPI dependency injection
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session and ensure it is closed afterwards."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
