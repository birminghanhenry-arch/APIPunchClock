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
from datetime import date, datetime, time, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models         import Employee, Assignment, Schedule, ClockRecord
from app.core.utils     import time_to_minutes, fmt_time
from app.core.constants import EVENT_NAME_TO_ID, EVENT_ID_TO_NAME, STATUS_NAME_TO_ID, STATUS_ID_TO_NAME
from app.repositories   import employee_repo, clock_repo

# Umbrales para detectar turno nocturno y cruce de medianoche.
# Un horario que comienza ≥ 20:00 se trata como nocturno.
# Una hora actual < 10:00 indica madrugada (cruce de medianoche).
_NIGHT_ENTRY_MIN    = 1200   # 20:00 en minutos
_MIDNIGHT_CUTOFF    = 600    # 10:00 en minutos
_CHECKOUT_LOOKBACK  = 10     # buscar ayer si check_out antes de esta hora


# ── Lógica pura (sin BD, testeable sin session) ───────────────────────────────

def _night_adjusted(entry_min: int, now_minutes: int) -> int:
    """
    Devuelve now_minutes ajustado para horarios nocturnos.

    Si el horario empieza ≥ 20:00 y la hora actual es < 10:00, el empleado
    ha cruzado medianoche: sumar 1440 para que la comparación sea correcta.

    Sin ajuste:  00:05 = 5 min < 1320 + 10 → on_time  (incorrecto)
    Con ajuste:  00:05 = 5 + 1440 = 1445 min > 1330    → late     (correcto)
    """
    if entry_min >= _NIGHT_ENTRY_MIN and now_minutes < _MIDNIGHT_CUTOFF:
        return now_minutes + 1440
    return now_minutes


def calculate_status(now_minutes: int, schedule: Schedule) -> tuple[str, time]:
    """
    Retorna (status_name, clock_time).
    A tiempo → clock_time = hora del horario (normalizada).
    Tardanza → clock_time = hora real.
    """
    entry_min     = time_to_minutes(schedule.check_in_time)
    effective_now = _night_adjusted(entry_min, now_minutes)
    if effective_now <= entry_min + schedule.tolerance_minutes:
        return "on_time", schedule.check_in_time
    h, m = divmod(now_minutes, 60)
    return "late", time(h, m)


def pick_active_jornada(assignments: list[Assignment], now_minutes: int) -> Schedule:
    """
    Elige la jornada activa en turno partido.
    Usa el punto medio entre las dos entradas como criterio.

    Si la segunda jornada es nocturna y now es madrugada, ajusta now_minutes
    para que el punto medio compare correctamente sin el salto de medianoche.
    """
    sorted_a = sorted(assignments, key=lambda a: time_to_minutes(a.schedule.check_in_time))
    if len(sorted_a) == 1:
        return sorted_a[0].schedule
    min1 = time_to_minutes(sorted_a[0].schedule.check_in_time)
    min2 = time_to_minutes(sorted_a[1].schedule.check_in_time)
    # Si la jornada más tardía es nocturna, normalizar now para evitar
    # que la madrugada se confunda con horario anterior al punto medio.
    effective_now = _night_adjusted(min2, now_minutes)
    midpoint      = min1 + (min2 - min1) // 2
    return sorted_a[1].schedule if effective_now >= midpoint else sorted_a[0].schedule


# ── Orquestación principal ────────────────────────────────────────────────────

def register_clock_event(db: Session, employee_id: int, event_type: str) -> ClockRecord:
    """
    Registra un marcaje.  Flujo:
        1. repo: buscar empleado
        2. validar lógica del día (con soporte de turno nocturno)
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
    work_date     = today

    # Turno nocturno: el check_out llega en madrugada del día siguiente.
    # Si no hay registros para hoy y la hora es temprana, buscamos ayer para
    # encontrar el check_in de la noche anterior y usar su work_date.
    if (
        not today_records
        and event_type == "check_out"
        and now_time.hour < _CHECKOUT_LOOKBACK
    ):
        yesterday      = today - timedelta(days=1)
        prev_records   = clock_repo.get_today_by_employee(db, employee_id, yesterday)
        if prev_records and prev_records[0].event_type == 1:
            # Hay un check_in abierto de ayer → es un checkout de turno nocturno.
            # El registro se guarda con el work_date del check_in para que el
            # agrupamiento por jornada (CSV pivot, reportes) sea coherente.
            today_records = prev_records
            work_date     = yesterday

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
        work_date   = work_date,
        clock_time  = clock_time,
        real_time   = now_time,
    )
    return clock_repo.save(db, record)
