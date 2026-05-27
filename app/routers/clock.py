"""
app/routers/clock.py  —  C de MVC
Endpoints de marcaje. Delega toda la lógica al service.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database  import get_db
from app.core.utils     import fmt_time
from app.schemas        import ClockRequest, ClockRecordOut
from app.services       import register_clock_event, EVENT_ID_TO_NAME, STATUS_ID_TO_NAME
from app.repositories   import clock_repo

router = APIRouter(prefix="/clock", tags=["Clock"])


@router.post("", response_model=ClockRecordOut)
def clock_in_out(req: ClockRequest, db: Session = Depends(get_db)):
    record = register_clock_event(db, req.employee_id, req.event_type)
    emp    = record.employee   # cargado por el repo dentro del service

    return ClockRecordOut(
        id            = record.id,
        employee_id   = emp.id,
        employee_name = emp.full_name,
        department    = emp.department.name,
        event_type    = req.event_type,
        status        = STATUS_ID_TO_NAME.get(record.status, "on_time"),
        work_date     = str(record.work_date),
        clock_time    = fmt_time(record.clock_time),
        real_time     = fmt_time(record.real_time),
        created_at    = record.created_at.isoformat(),
    )


@router.get("/today", response_model=list[ClockRecordOut])
def get_today(
    employee_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    records = clock_repo.get_today_all(db, date.today(), employee_id)
    return [
        ClockRecordOut(
            id            = r.id,
            employee_id   = r.employee_id,
            employee_name = r.employee.full_name,
            department    = r.employee.department.name,
            event_type    = EVENT_ID_TO_NAME.get(r.event_type, ""),
            status        = STATUS_ID_TO_NAME.get(r.status, "on_time"),
            work_date     = str(r.work_date),
            clock_time    = fmt_time(r.clock_time),
            real_time     = fmt_time(r.real_time),
            created_at    = r.created_at.isoformat(),
        )
        for r in records
    ]
