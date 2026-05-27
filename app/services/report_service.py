"""
app/services/report_service.py  —  S de MVC
Lógica de estadísticas y generación de CSV.

Recibe datos del repository, los procesa y retorna estructuras limpias.
No hace queries directas a la BD.
"""
from __future__ import annotations
import csv, io
from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models        import Employee
from app.core.utils    import fmt_time
from app.repositories  import clock_repo

EVENT_ID_TO_NAME  = {1: "check_in",  2: "check_out"}
STATUS_ID_TO_NAME = {1: "on_time",   2: "late",    3: "flexible"}


# ── Estadísticas del día ──────────────────────────────────────────────────────

def get_today_stats(db: Session) -> dict:
    today       = date.today()
    total       = db.query(Employee).filter(Employee.active == True).count()
    check_ins   = clock_repo.get_check_ins_for_date(db, today)

    active_set  = {r.employee_id for r in check_ins}
    late_set    = {r.employee_id for r in check_ins if r.status == 2}
    on_time_set = {r.employee_id for r in check_ins if r.status == 1}
    active      = len(active_set)

    return {
        "total_employees": total,
        "active_today":    active,
        "late_today":      len(late_set),
        "absent_today":    total - active,
        "on_time_rate":    round(len(on_time_set) / active * 100, 1) if active else 0.0,
    }


# ── Reporte diario ────────────────────────────────────────────────────────────

def get_daily_report(db: Session, days: int) -> list[dict]:
    today      = date.today()
    start_date = today - timedelta(days=days - 1)
    total      = db.query(Employee).filter(Employee.active == True).count()
    records    = clock_repo.get_check_ins_range(db, start_date, today)

    day_map: dict[str, dict] = {}
    for offset in range(days):
        d = start_date + timedelta(days=offset)
        if d.weekday() < 6:
            day_map[str(d)] = {"date": str(d), "present": 0, "late": 0, "absent": 0}

    for r in records:
        key = str(r.work_date)
        if key in day_map:
            day_map[key]["present"] += 1
            if r.status == 2:
                day_map[key]["late"] += 1

    result = []
    for key, row in sorted(day_map.items()):
        row["absent"] = max(0, total - row["present"])
        result.append(row)
    return result


# ── Exportación CSV ───────────────────────────────────────────────────────────

def generate_csv(db: Session, since: str | None, until: str | None) -> tuple[io.StringIO, str]:
    """Genera CSV en memoria. Retorna (buffer, filename)."""
    today      = date.today()
    date_since = date.fromisoformat(since) if since else today - timedelta(days=7)
    date_until = date.fromisoformat(until) if until else today

    records = clock_repo.get_range(db, date_since, date_until)
    rows    = _pivot(records)

    buf = io.StringIO()
    w   = csv.writer(buf)
    w.writerow(["Empleado", "Departamento", "Fecha", "Entrada", "Salida", "Estado", "Tardanza"])
    for row in rows:
        w.writerow([row["employee"], row["department"], row["date"],
                    row["check_in"], row["check_out"], row["status"], row["late"]])
    buf.seek(0)
    return buf, f"asistencia_{date_since}_{date_until}.csv"


def _pivot(records) -> list[dict]:
    """Agrupa (empleado, fecha) → una fila con check_in y check_out."""
    pivot: dict[tuple, dict] = {}
    for r in records:
        key = (r.employee_id, str(r.work_date))
        if key not in pivot:
            pivot[key] = {
                "employee":   r.employee.full_name,
                "department": r.employee.department.name,
                "date":       str(r.work_date),
                "check_in": "", "check_out": "", "status": "", "late": "",
            }
        et = EVENT_ID_TO_NAME.get(r.event_type, "")
        if et == "check_in":
            pivot[key]["check_in"] = fmt_time(r.real_time)[:5]
            pivot[key]["status"]   = STATUS_ID_TO_NAME.get(r.status, "")
            pivot[key]["late"]     = "Sí" if r.status == 2 else "No"
        elif et == "check_out":
            pivot[key]["check_out"] = fmt_time(r.real_time)[:5]
    return list(pivot.values())
