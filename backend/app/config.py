from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or a .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- Database -----
    DATABASE_URL: str = "sqlite+aiosqlite:///./eduflow.db"

    # ----- Auth / JWT -----
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # ----- Application -----
    APP_NAME: str = "EduFlow"
    DEBUG: bool = False
    BASE_URL: str = "http://localhost:8000"
    FRONTEND_ORIGINS: str = "http://localhost:8080,http://127.0.0.1:8080"

    # ----- AI / Gemini -----
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL_NAME: str = "gemini-flash-latest"
    GEMINI_API_BASE_URL: str = "https://generativelanguage.googleapis.com"
    GEMINI_TIMEOUT_SECONDS: float = 30.0
    AI_MAX_RETRIES: int = 3
    AI_RETRY_BASE_DELAY_SECONDS: float = 0.5
    AI_ADMIN_REPORT_CACHE_TTL_SECONDS: int = 3600
    AI_ADMIN_REPORT_PROMPT_VERSION: str = "v1"
    AI_ADMIN_REPORT_USER_RATE_LIMIT: int = 3
    AI_ADMIN_REPORT_INSTITUTION_RATE_LIMIT: int = 10
    AI_ADMIN_REPORT_RATE_LIMIT_WINDOW_SECONDS: int = 600
    AI_ADMIN_REPORT_STALE_AFTER_SECONDS: int = 900
    AI_STUDENT_EXPLANATION_PROMPT_VERSION: str = "v1"
    AI_STUDENT_EXPLANATION_CACHE_TTL_SECONDS: int = 86400
    AI_STUDENT_EXPLANATION_USER_RATE_LIMIT: int = 12
    AI_STUDENT_EXPLANATION_RATE_LIMIT_WINDOW_SECONDS: int = 600
    AI_STUDENT_EXPLANATION_STALE_AFTER_SECONDS: int = 900
    AI_RATE_LIMIT_BACKEND: str = "database"
    AI_RATE_LIMIT_COUNTER_RETENTION_SECONDS: int = 86400

    # ----- Infrastructure (Residual) -----
    # Redis and Celery have been removed from the architecture.
    SUPPORT_RERUN_LIMIT_PER_DAY: int = 3

    # ----- Scheduled reports -----
    SCHEDULED_REPORT_LOOKAHEAD_SECONDS: int = 120

    # ----- Email (optional) -----
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_USE_TLS: bool = True

    @property
    def frontend_origins(self) -> List[str]:
        return [origin.strip() for origin in self.FRONTEND_ORIGINS.split(",") if origin.strip()]


settings = Settings()