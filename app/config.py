
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    MODEL_NAME: str = "mock-001"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
