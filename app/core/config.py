"""
app/core/config.py
Configuración centralizada via variables de entorno (.env).
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str  = "postgresql+psycopg://postgres:postgres@localhost:5432/apipunchclock"
    APP_TITLE:    str  = "PunchClock API"
    APP_VERSION:  str  = "2.0.0"
    DEBUG:        bool = False
    CORS_ORIGINS: list[str] = ["*"]
    DEFAULT_TOLERANCE_MINUTES:  int = 10
    FLEXIBLE_TOLERANCE_MINUTES: int = 15
    SECRET_KEY:                 str = "cambia-este-valor-en-produccion"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
