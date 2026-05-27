"""
app/models/department.py  —  M de MVC
Department y Shift.  Solo columnas y relaciones — cero lógica.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.base import Base


class Department(Base):
    __tablename__ = "departments"

    id   = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    employees = relationship("Employee", back_populates="department")


class Shift(Base):
    __tablename__ = "shifts"

    id   = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=False)

    schedules = relationship("Schedule", back_populates="shift")
