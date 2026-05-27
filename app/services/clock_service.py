"""
app/services/clock_service.py  —  S de MVC
Lógica de negocio para marcajes.

Responsabilidades:
    - Validar el estado previo del día (no doble entrada)
    - Elegir la jornada correcta en turno partido
    - Calcular si la llegada es a tiempo o tardanza
    - Construir el ClockRecord y pedir al repo que lo persista

NO hace queries directas a la BD.  Delega en repositories/.
"""
from __future__ import annotations
from datetime import date, datetime, time
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models         import Employee, Assignment, Schedule, ClockRecord
from app.core.utils     import time_to_minutes, fmt_time
from app.repositories   import employee_repo, clock_repo

# ── Mapas de referencia ───────────────────────────────────────────────────────
EVENT_NAME_TO_ID  = {"check_in": 1, "check_out": 2}
EVENT_ID_TO_NAME  = {1: "check_in",  2: "check_out"}
STATUS_NAME_TO_ID = {"on_time": 1, "late": 2, "flexible": 3}
STATUS_ID_TO_NAME = {1: "on_time",   2: "late",    3: "flexible"}


# ── Lógica pura (sin BD, testeable sin session) ───────────────────────────────

def calculate_status(now_minutes: int, schedule: Schedule) -> tuple[str, time]:
    """
    Retorna (status_name, clock_time).
    A tiempo  → clock_time = hora del horario (normalizada).
    Tardanza  → clock_time = hora real.
    """
    entry_min = time_to_minutes(schedule.check_in_time)
    if now_minutes <= entry_min + schedule.tolerance_minutes:
        return "on_time", schedule.check_in_time
    h, m = divmod(now_minutes, 60)
    return "late", time(h, m)


def pick_active_jornada(assignments: list[Assignment], now_minutes: int) -> Schedule:
    """
    Elige la jornada activa en turno partido.
    Usa el punto medio entre las dos entradas como criterio.
    """
    sorted_a = sorted(assignments, key=lambda a: time_to_minutes(a.schedule.check_in_time))
    if len(sorted_a) == 1:
        return sorted_a[0].schedule
    min1 = time_to_minutes(sorted_a[0].schedule.check_in_time)
    min2 = time_to_minutes(sorted_a[1].schedule.check_in_time)
    midpoint = min1 + (min2 - min1) // 2
    return sorted_a[1].schedule if now_minutes >= midpoint else sorted_a[0].schedule


# ── Orquestación principal ────────────────────────────────────────────────────

def register_clock_event(db: Session, employee_id: int, event_type: str) -> ClockRecord:
    """
    Registra un marcaje.  Flujo:
        1. repo: buscar empleado
        2. validar lógica del día
        3. calcular estado (lógica pura)
        4. repo: persistir y retornar
    """
    # 1 — Buscar empleado (via repo, no query directa)
    emp = employee_repo.get_by_id(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    event_id = EVENT_NAME_TO_ID.get(event_type)
    if not event_id:
        raise HTTPException(status_code=400, detail="event_type inválido")

    now      = datetime.now()
    today    = now.date()
    now_time = now.time()
    now_min  = time_to_minutes(now_time)

    # 2 — Validar estado previo del día (via repo)
    today_records = clock_repo.get_today_by_employee(db, employee_id, today)
    last = today_records[0] if today_records else None

    if event_type == "check_in"  and last and last.event_type == 1:
        raise HTTPException(status_code=409, detail="Ya tiene una entrada registrada")
    if event_type == "check_out" and (not last or last.event_type == 2):
        raise HTTPException(status_code=409, detail="Debe registrar entrada primero")

    # 3 — Calcular estado (lógica pura, sin BD)
    if event_type == "check_out":
        status_name, clock_time = "on_time", now_time

    elif emp.schedule_type == "flexible":
        status_name, clock_time = "flexible", now_time

    else:
        day_assignments = employee_repo.get_assignments_for_date(db, emp.id, today)
        if not day_assignments:
            status_name, clock_time = "flexible", now_time
        else:
            active_sched = pick_active_jornada(day_assignments, now_min)
            status_name, clock_time = calculate_status(now_min, active_sched)

    # 4 — Persistir (via repo)
    record = ClockRecord(
        employee_id = emp.id,
        event_type  = event_id,
        status      = STATUS_NAME_TO_ID[status_name],
        work_date   = today,
        clock_time  = clock_time,
        real_time   = now_time,
    )
    return clock_repo.save(db, record)
