"""
app/database/seeders/assignment_seeder.py
Asignaciones diarias para los últimos N días hábiles.
"""
import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import Employee, Assignment
from app.database.fixtures import DEPT_SCHEDULE_MAP


def seed_assignments(session: Session, employees: list[Employee], *, days_back: int = 30, seed_value: int = 42, verbose: bool = True) -> int:
    random.seed(seed_value)
    today = date.today()
    start = today - timedelta(days=days_back)
    emp_by_dept = {}
    for e in employees:
        emp_by_dept.setdefault(e.department_id, []).append(e)

    objs, count = [], 0
    for offset in range(days_back + 1):
        d = start + timedelta(days=offset)
        if d.weekday() == 6: continue
        for dept_id, (prim, sec) in DEPT_SCHEDULE_MAP.items():
            for emp in emp_by_dept.get(dept_id, []):
                objs.append(Assignment(employee_id=emp.id, schedule_id=random.choice(prim), work_date=d))
                count += 1
                if sec:
                    objs.append(Assignment(employee_id=emp.id, schedule_id=random.choice(sec), work_date=d))
                    count += 1

    session.bulk_save_objects(objs)
    try:
        session.commit()
    except Exception:
        session.rollback()
    if verbose: print(f"  [assignments] {count} insertadas")
    return count
