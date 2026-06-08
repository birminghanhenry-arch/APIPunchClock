"""
app/routers/auth.py  —  C de MVC (Controller)
Solo maneja HTTP: recibe request, llama al repositorio, retorna response.
Sin lógica de negocio ni queries directas.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database  import get_db
from app.core.security  import create_access_token
from app.schemas        import LoginRequest, EmployeeOut, LoginResponse
from app.repositories   import employee_repo

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    emp = employee_repo.get_by_pin(db, req.pin)
    if not emp:
        raise HTTPException(status_code=401, detail="PIN incorrecto")

    employee_out = EmployeeOut(
        id=emp.id, full_name=emp.full_name,
        department=emp.department.name, department_id=emp.department_id,
        initials=emp.initials, schedule_type=emp.schedule_type,
        tolerance_minutes=emp.tolerance_minutes,
        is_admin=emp.is_admin, active=emp.active,
    )
    return LoginResponse(
        access_token=create_access_token(emp.id, emp.is_admin),
        employee=employee_out,
    )
