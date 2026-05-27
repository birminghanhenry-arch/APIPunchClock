"""
app/core/base.py
Base declarativa de SQLAlchemy.

Un solo Base para todo el proyecto.
Todos los modelos importan desde aquí — nunca declaran su propio Base.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
