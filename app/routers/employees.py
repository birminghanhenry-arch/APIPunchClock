"""
app/routers/employees.py  —  C de MVC
Endpoints de empleados. Solo HTTP + mapeo a schemas.
"""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database  import get_db
from app.core.security  import get_current_user
from app.core.utils     import time_to_minutes, fmt_time
from app.schemas        import EmployeeOut, AssignmentOut, ScheduleOut
from app.repositories   import employee_repo
from app.models         import Schedule

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("", response_model=list[EmployeeOut])
def list_employees(
    db: Session = Depends(get_db),
    _:  object  = Depends(get_current_user),
):
    return [
        EmployeeOut(
            id=e.id, full_name=e.full_name,
            department=e.department.name, department_id=e.department_id,
            initials=e.initials, schedule_type=e.schedule_type,
            tolerance_minutes=e.tolerance_minutes,
            is_admin=e.is_admin, active=e.active,
        )
        for e in employee_repo.list_active(db)
    ]


@router.get("/{employee_id}/assignment", response_model=AssignmentOut)
def get_assignment(
    employee_id: int,
    work_date: str = Query(default=None, description="YYYY-MM-DD (default: hoy)"),
    db: Session = Depends(get_db),
    _:  object  = Depends(get_current_user),
):
    target = date.fromisoformat(work_date) if work_date else date.today()
    assignments = employee_repo.get_assignments_for_date(db, employee_id, target)

    if not assignments:
        return AssignmentOut(jornada1=None, jornada2=None)

    assignments.sort(key=lambda a: time_to_minutes(a.schedule.check_in_time))

    def to_schema(s: Schedule) -> ScheduleOut:
        return ScheduleOut(
            id=s.id,
            check_in_time=fmt_time(s.check_in_time),
            check_out_time=fmt_time(s.check_out_time),
            tolerance_minutes=s.tolerance_minutes,
            shift_name=s.shift.name,
        )

    return AssignmentOut(
        jornada1=to_schema(assignments[0].schedule),
        jornada2=to_schema(assignments[1].schedule) if len(assignments) > 1 else None,
    )
