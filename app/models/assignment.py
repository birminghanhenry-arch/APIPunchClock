"""
app/models/assignment.py  —  M de MVC
Asignación diaria empleado ↔ horario ↔ fecha.
El UNIQUE incluye schedule_id para permitir doble jornada.
"""
import uuid
from sqlalchemy import Column, String, Integer, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.base import Base


class Assignment(Base):
    __tablename__ = "assignments"
    __table_args__ = (
        UniqueConstraint("employee_id", "schedule_id", "work_date", name="uq_assignment"),
    )

    id          = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False)
    work_date   = Column(Date, nullable=False)

    employee = relationship("Employee", back_populates="assignments")
    schedule = relationship("Schedule", back_populates="assignments")
