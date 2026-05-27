"""
app/models/clock.py  —  M de MVC
ClockRecord y sus tablas de referencia.

clock_time  → hora normalizada (hora del horario si llegó a tiempo)
real_time   → hora real del reloj (para reportes RRHH)
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base


class ClockEventType(Base):
    __tablename__ = "clock_event_types"
    id   = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)   # check_in | check_out


class ClockStatus(Base):
    __tablename__ = "clock_statuses"
    id   = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)   # on_time | late | flexible


class ClockRecord(Base):
    __tablename__ = "clock_records"

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(Integer, ForeignKey("employees.id"),        nullable=False)
    event_type  = Column(Integer, ForeignKey("clock_event_types.id"), nullable=False)
    status      = Column(Integer, ForeignKey("clock_statuses.id"),    nullable=False)
    work_date   = Column(Date,     nullable=False)
    clock_time  = Column(Time,     nullable=False)
    real_time   = Column(Time,     nullable=False)
    created_at  = Column(DateTime, nullable=False, default=datetime.utcnow)

    employee   = relationship("Employee",       back_populates="clocks")
    event_rel  = relationship("ClockEventType")
    status_rel = relationship("ClockStatus")
