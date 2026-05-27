"""
app/database/seeders/employee_seeder.py
Genera empleados ficticios con Faker. Solo dev/staging.
"""
import random
from faker import Faker
from sqlalchemy.orm import Session
from app.models import Employee
from app.database.fixtures import DEPT_SCHEDULE_MAP

fake = Faker("es_MX")

EMP_COUNTS    = {1:12, 2:4, 3:10, 4:3, 5:5, 6:2, 7:3, 8:3, 9:2, 10:3}
FLEXIBLE_DEPTS = {5, 6}
ADMIN_DEPTS    = {9}


def seed_employees(session: Session, *, seed_value: int = 42, verbose: bool = True) -> list[Employee]:
    if session.query(Employee).count() > 0:
        if verbose: print("  [employees] ya existen, omitiendo")
        return session.query(Employee).all()

    fake.seed_instance(seed_value); random.seed(seed_value)
    used, objs, emp_id = set(), [], 1

    for dept_id, count in EMP_COUNTS.items():
        for i in range(count):
            while (pin := str(random.randint(1000, 9999))) in used: pass
            used.add(pin)
            objs.append(Employee(
                id=emp_id, full_name=fake.name().upper(),
                department_id=dept_id, pin=pin,
                schedule_type="flexible" if dept_id in FLEXIBLE_DEPTS else "fixed",
                tolerance_minutes=15 if dept_id in FLEXIBLE_DEPTS else 10,
                is_admin=(dept_id in ADMIN_DEPTS and i == 0),
                active=True,
            ))
            emp_id += 1

    session.bulk_save_objects(objs)
    session.commit()
    if verbose: print(f"  [employees] {len(objs)} insertados")
    return session.query(Employee).all()
