"""App config — all values from environment, fails without DATABASE_URL."""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    ENVIRONMENT: str = "local"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("DATABASE_URL")
    @classmethod
    def nonempty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("DATABASE_URL required — cp .env.example .env")
        return v


_cfg: Settings | None = None


def get_settings() -> Settings:
    global _cfg
    if _cfg is None:
        _cfg = Settings()  # type: ignore[call-arg]
    return _cfg
