"""
app/core/utils.py
Utilidades puras de tiempo.  Sin lógica de negocio, sin imports de modelos.
Usadas por services, seeders y scripts.
"""
from datetime import date, datetime, time, timedelta


def time_to_minutes(t: time) -> int:
    """Convierte time → minutos desde medianoche."""
    return t.hour * 60 + t.minute


def add_minutes(t: time, minutes: int) -> time:
    """Suma o resta minutos a un objeto time."""
    return (datetime.combine(date.today(), t) + timedelta(minutes=minutes)).time()


def fmt_time(t: time | None) -> str:
    """Formatea time como 'HH:MM:SS'. Retorna '' si es None."""
    return t.strftime("%H:%M:%S") if t else ""
