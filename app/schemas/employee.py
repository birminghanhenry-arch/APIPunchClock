"""
app/schemas/employee.py
Schemas de entrada y salida para empleados y asignaciones.
"""
from __future__ import annotations
from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    pin: str

    @field_validator("pin")
    @classmethod
    def pin_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("PIN no puede estar vacío")
        return v.strip()


class EmployeeOut(BaseModel):
    id:                int
    full_name:         str
    department:        str
    department_id:     int
    initials:          str
    schedule_type:     str
    tolerance_minutes: int
    is_admin:          bool
    active:            bool

    model_config = {"from_attributes": True}


class ScheduleOut(BaseModel):
    id:                int
    check_in_time:     str
    check_out_time:    str
    tolerance_minutes: int
    shift_name:        str

    model_config = {"from_attributes": True}


class AssignmentOut(BaseModel):
    """Hasta dos jornadas por día. jornada2 = None si no hay turno partido."""
    jornada1: ScheduleOut | None
    jornada2: ScheduleOut | None


class LoginResponse(BaseModel):
    """Respuesta de login: token JWT + datos del empleado."""
    access_token: str
    token_type:   str = "bearer"
    employee:     EmployeeOut
