"""
app/database/seeders/clock_seeder.py
Simula historial de marcajes. 85% puntual, 12% tarde, 3% ausente.
"""
import random
from datetime import date
from sqlalchemy.orm import Session
from app.models import Employee, Assignment, Schedule, ClockRecord
from app.core.utils import time_to_minutes, add_minutes


def seed_clock_records(session: Session, employees: list[Employee], *, seed_value: int = 42, verbose: bool = True) -> int:
    random.seed(seed_value)
    today     = date.today()
    sched_map = {s.id: s for s in session.query(Schedule).all()}
    emp_map   = {e.id: e for e in employees}

    date_map = {}
    for a in session.query(Assignment).filter(Assignment.work_date < today).all():
        date_map.setdefault(a.work_date, []).append(a)

    total = 0
    for work_date in sorted(date_map):
        records = []
        by_emp  = {}
        for a in date_map[work_date]:
            by_emp.setdefault(a.employee_id, []).append(a)

        for emp_id, asgns in by_emp.items():
            emp = emp_map.get(emp_id)
            if not emp or not emp.active: continue
            asgns.sort(key=lambda a: sched_map[a.schedule_id].check_in_time)
            for asgn in asgns:
                sched = sched_map[asgn.schedule_id]
                roll  = random.random()
                if roll < 0.03: continue
                if roll < 0.88:
                    offset = random.randint(-8, sched.tolerance_minutes - 1)
                    status_id, real_in, clock_in = 1, add_minutes(sched.check_in_time, offset), sched.check_in_time
                else:
                    offset = sched.tolerance_minutes + random.randint(1, 40)
                    status_id, real_in = 2, add_minutes(sched.check_in_time, offset)
                    clock_in = real_in
                records.append(ClockRecord(employee_id=emp_id, event_type=1, status=status_id,
                                            work_date=work_date, clock_time=clock_in, real_time=real_in))
                if random.random() < 0.90:
                    real_out = add_minutes(sched.check_out_time, random.randint(-5, 30))
                    records.append(ClockRecord(employee_id=emp_id, event_type=2, status=1,
                                                work_date=work_date, clock_time=real_out, real_time=real_out))
        session.bulk_save_objects(records)
        session.commit()
        total += len(records)

    if verbose: print(f"  [clock_records] {total} marcajes generados")
    return total
