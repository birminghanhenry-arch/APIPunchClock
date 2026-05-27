"""
app/core/config.py
Configuración centralizada via variables de entorno (.env).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str  = "sqlite:///./punchclock.db"
    APP_TITLE:    str  = "PunchClock API"
    APP_VERSION:  str  = "2.0.0"
    DEBUG:        bool = False
    CORS_ORIGINS: list[str] = ["*"]
    DEFAULT_TOLERANCE_MINUTES:  int = 10
    FLEXIBLE_TOLERANCE_MINUTES: int = 15

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
