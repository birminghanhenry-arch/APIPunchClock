"""
app/database/seeders/reference_seeder.py
Carga catálogos fijos. Idempotente (ON CONFLICT DO NOTHING).
"""
from sqlalchemy.orm import Session
from app.models import Department, Shift, Schedule, ClockEventType, ClockStatus
from app.database.fixtures import (
    DEPARTMENTS, SHIFTS, SCHEDULES, CLOCK_EVENT_TYPES, CLOCK_STATUSES,
)


def seed_reference_data(session: Session, *, verbose: bool = True) -> None:
    def existing(model): return {r.id for r in session.query(model.id).all()}

    added = 0
    for id_, name in DEPARTMENTS:
        if id_ not in existing(Department):
            session.add(Department(id=id_, name=name)); added += 1
    for id_, name in SHIFTS:
        if id_ not in existing(Shift):
            session.add(Shift(id=id_, name=name)); added += 1
    for id_, shift_id, ci, co, tol in SCHEDULES:
        if id_ not in existing(Schedule):
            session.add(Schedule(id=id_, shift_id=shift_id,
                                  check_in_time=ci, check_out_time=co,
                                  tolerance_minutes=tol)); added += 1
    for id_, name in CLOCK_EVENT_TYPES:
        if id_ not in existing(ClockEventType):
            session.add(ClockEventType(id=id_, name=name)); added += 1
    for id_, name in CLOCK_STATUSES:
        if id_ not in existing(ClockStatus):
            session.add(ClockStatus(id=id_, name=name)); added += 1

    session.commit()
    if verbose:
        print(f"  [reference_data] {added} registros insertados")
