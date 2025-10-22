# app/config.py
from __future__ import annotations

from datetime import UTC, datetime

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    model: str = "demo-xyz-2"

    # read .env at project root; ignore extra keys
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

settings = Settings()
