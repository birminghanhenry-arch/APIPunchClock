"""
app/repositories/clock_repo.py
Todas las queries relacionadas con marcajes.

Regla: solo habla con la BD.
No valida lógica de negocio, no lanza HTTPException.
"""
from datetime import date
from sqlalchemy.orm import Session, joinedload

from app.models import ClockRecord, Employee


def get_today_by_employee(db: Session, employee_id: int, today: date) -> list[ClockRecord]:
    """Marcajes del empleado en `today`, orden descendente por timestamp."""
    return (
        db.query(ClockRecord)
        .filter(
            ClockRecord.employee_id == employee_id,
            ClockRecord.work_date   == today,
        )
        .order_by(ClockRecord.created_at.desc())
        .all()
    )


def get_today_all(db: Session, today: date, employee_id: int | None = None) -> list[ClockRecord]:
    """Todos los marcajes del día. Opcionalmente filtrado por empleado."""
    q = (
        db.query(ClockRecord)
        .options(joinedload(ClockRecord.employee).joinedload(Employee.department))
        .filter(ClockRecord.work_date == today)
    )
    if employee_id:
        q = q.filter(ClockRecord.employee_id == employee_id)
    return q.order_by(ClockRecord.created_at.desc()).all()


def get_range(db: Session, date_since: date, date_until: date) -> list[ClockRecord]:
    """Marcajes en un rango de fechas, ordenados para export."""
    return (
        db.query(ClockRecord)
        .options(joinedload(ClockRecord.employee).joinedload(Employee.department))
        .filter(
            ClockRecord.work_date >= date_since,
            ClockRecord.work_date <= date_until,
        )
        .order_by(ClockRecord.work_date, ClockRecord.employee_id, ClockRecord.created_at)
        .all()
    )


def get_check_ins_for_date(db: Session, today: date) -> list[ClockRecord]:
    """Solo entradas del día (para estadísticas)."""
    return (
        db.query(ClockRecord)
        .filter(ClockRecord.work_date == today, ClockRecord.event_type == 1)
        .all()
    )


def get_check_ins_range(db: Session, date_since: date, date_until: date) -> list[ClockRecord]:
    """Solo entradas en un rango de fechas (para reporte diario)."""
    return (
        db.query(ClockRecord)
        .filter(
            ClockRecord.work_date  >= date_since,
            ClockRecord.work_date  <= date_until,
            ClockRecord.event_type == 1,
        )
        .all()
    )


def get_between_dates(db: Session, start_date: date, end_date: date) -> list[ClockRecord]:
    """Marcajes en un rango de fechas, orden descendente para tablas."""
    return (
        db.query(ClockRecord)
        .options(joinedload(ClockRecord.employee).joinedload(Employee.department))
        .filter(
            ClockRecord.work_date >= start_date,
            ClockRecord.work_date <= end_date,
        )
        .order_by(ClockRecord.work_date.desc(), ClockRecord.created_at.desc())
        .all()
    )


def save(db: Session, record: ClockRecord) -> ClockRecord:
    """Persiste un nuevo marcaje y lo retorna con su id asignado."""
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
