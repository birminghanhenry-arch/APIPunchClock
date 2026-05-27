"""
app/database/seeders/__init__.py
Orquesta seeders en el orden correcto (respeta foreign keys).
"""
from sqlalchemy.orm import Session
from app.database.seeders.reference_seeder  import seed_reference_data
from app.database.seeders.employee_seeder   import seed_employees
from app.database.seeders.assignment_seeder import seed_assignments
from app.database.seeders.clock_seeder      import seed_clock_records


def run_all(session: Session, *, verbose: bool = True) -> None:
    if verbose: print("\n── Seeders ────────────────────────────────────────")
    seed_reference_data(session, verbose=verbose)
    employees = seed_employees(session, verbose=verbose)
    seed_assignments(session, employees, verbose=verbose)
    seed_clock_records(session, employees, verbose=verbose)
    if verbose: print("── Completado ─────────────────────────────────────\n")
