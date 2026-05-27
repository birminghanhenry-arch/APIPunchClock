"""
app/models/employee.py  —  M de MVC
Empleado.  La propiedad `initials` es la única lógica permitida en el modelo
(derivada 100% de sus propios campos, sin acceso a BD).
"""
from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from app.core.base import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("schedule_type IN ('fixed', 'flexible')", name="ck_schedule_type"),
    )

    id                = Column(Integer, primary_key=True)
    full_name         = Column(String(100), nullable=False)
    department_id     = Column(Integer, ForeignKey("departments.id"), nullable=False)
    pin               = Column(String(10), nullable=False, unique=True)
    schedule_type     = Column(String(10), nullable=False, default="fixed")
    tolerance_minutes = Column(Integer, nullable=False, default=10)
    is_admin          = Column(Boolean, nullable=False, default=False)
    active            = Column(Boolean, nullable=False, default=True)

    department  = relationship("Department", back_populates="employees")
    assignments = relationship("Assignment", back_populates="employee")
    clocks      = relationship("ClockRecord", back_populates="employee")

    @property
    def initials(self) -> str:
        parts = self.full_name.split()
        return "".join(p[0] for p in parts[:2]).upper()
