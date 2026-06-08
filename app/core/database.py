"""
app/core/database.py
Engine, SessionLocal y dependencia get_db para FastAPI.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings


def _build_engine():
    return create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,   # descarta conexiones caídas antes de usarlas
    )


engine       = _build_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    """
    Dependencia FastAPI — una sesión por request.

        def endpoint(db: Session = Depends(get_db)): ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
