"""
app/models/schedule.py  —  M de MVC
Horario concreto: entrada, salida y tolerancia.
"""
from sqlalchemy import Column, Integer, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.core.base import Base


class Schedule(Base):
    __tablename__ = "schedules"

    id                = Column(Integer, primary_key=True)
    shift_id          = Column(Integer, ForeignKey("shifts.id"), nullable=False)
    check_in_time     = Column(Time, nullable=False)
    check_out_time    = Column(Time, nullable=False)
    tolerance_minutes = Column(Integer, nullable=False, default=10)

    shift       = relationship("Shift", back_populates="schedules")
    assignments = relationship("Assignment", back_populates="schedule")
