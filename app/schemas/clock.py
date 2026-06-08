"""
app/schemas/clock.py
Schemas de entrada y salida para marcajes.
"""
from pydantic import BaseModel, field_validator


class ClockRequest(BaseModel):
    event_type: str   # "check_in" | "check_out"

    @field_validator("event_type")
    @classmethod
    def valid_event(cls, v: str) -> str:
        if v not in ("check_in", "check_out"):
            raise ValueError("event_type debe ser 'check_in' o 'check_out'")
        return v


class ClockRecordOut(BaseModel):
    id:            str
    employee_id:   int
    employee_name: str
    department:    str
    event_type:    str
    status:        str
    work_date:     str
    clock_time:    str
    real_time:     str
    created_at:    str

    model_config = {"from_attributes": True}
