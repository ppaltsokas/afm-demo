# app/config.py
from __future__ import annotations
from datetime import datetime, timezone
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "local"
    model: str = "demo-xyz-2"

    # read .env at project root; ignore extra keys
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

settings = Settings()
