"""
app/schemas/reports.py
Schemas de salida para estadísticas y reportes.
"""
from pydantic import BaseModel


class StatsOut(BaseModel):
    total_employees: int
    active_today:    int
    late_today:      int
    absent_today:    int
    on_time_rate:    float


class DailyReportRow(BaseModel):
    date:    str
    present: int
    late:    int
    absent:  int
