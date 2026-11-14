
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Locate backend/.env regardless of where the script is executed.
BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):

    PROJECT_NAME: str = "Recruitment Management System"
    API_VERSION: str = "v1"

    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        extra="ignore"
    )


settings = Settings()
