"""
app/models/__init__.py
Registra todos los modelos en SQLAlchemy e importa Base.
El orden importa: tablas sin FK primero.
"""
from app.core.base import Base

from app.models.department import Department, Shift          # sin FK
from app.models.schedule   import Schedule                   # → Shift
from app.models.employee   import Employee                   # → Department
from app.models.assignment import Assignment                 # → Employee, Schedule
from app.models.clock      import ClockEventType, ClockStatus, ClockRecord  # → Employee

from app.core.database import engine


def create_tables() -> None:
    """Crea todas las tablas si no existen. Idempotente."""
    Base.metadata.create_all(bind=engine)


__all__ = [
    "Base",
    "Department", "Shift",
    "Schedule",
    "Employee",
    "Assignment",
    "ClockEventType", "ClockStatus", "ClockRecord",
    "create_tables",
]
