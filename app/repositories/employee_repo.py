"""
app/repositories/employee_repo.py
Todas las queries relacionadas con empleados y asignaciones.

Regla: esta capa solo habla con la BD.
No valida, no calcula lógica de negocio, no lanza HTTPException.
"""
from datetime import date
from sqlalchemy.orm import Session, joinedload

from app.models import Employee, Assignment, Schedule


def count_active(db: Session) -> int:
    """Total de empleados activos (para estadísticas y reportes)."""
    return db.query(Employee).filter(Employee.active == True).count()


def get_by_pin(db: Session, pin: str) -> Employee | None:
    return (
        db.query(Employee)
        .options(joinedload(Employee.department))
        .filter(Employee.pin == pin, Employee.active == True)
        .first()
    )


def get_by_id(db: Session, employee_id: int) -> Employee | None:
    return (
        db.query(Employee)
        .options(joinedload(Employee.department))
        .filter(Employee.id == employee_id)
        .first()
    )


def list_active(db: Session) -> list[Employee]:
    return (
        db.query(Employee)
        .options(joinedload(Employee.department))
        .filter(Employee.active == True)
        .order_by(Employee.department_id, Employee.full_name)
        .all()
    )


def get_assignments_for_date(
    db: Session,
    employee_id: int,
    work_date: date,
) -> list[Assignment]:
    return (
        db.query(Assignment)
        .options(joinedload(Assignment.schedule).joinedload(Schedule.shift))
        .filter(
            Assignment.employee_id == employee_id,
            Assignment.work_date   == work_date,
        )
        .all()
    )
