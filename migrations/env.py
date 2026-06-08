"""
migrations/env.py
Configuración del entorno Alembic.

Lee DATABASE_URL desde app.core.config (misma fuente que la aplicación)
y registra todos los modelos para que autogenerate los detecte.
"""
from __future__ import annotations
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Path al raíz del proyecto ─────────────────────────────────────────────────
# Necesario para que los imports de `app.*` funcionen desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── Configuración del proyecto ────────────────────────────────────────────────
from app.core.config import settings
from app.core.base   import Base

# Importar TODOS los modelos para que Base.metadata los registre.
# Sin estos imports, autogenerate no detectaría las tablas.
import app.models  # noqa: F401  (importa Department, Shift, Schedule, Employee, …)

# ── Alembic config ────────────────────────────────────────────────────────────
config = context.config

# Inyectar la URL desde settings (respeta .env)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata que Alembic usa para autogenerate
target_metadata = Base.metadata


# ── Modo offline (genera SQL sin conexión real) ───────────────────────────────

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ── Modo online (conexión real a la BD) ───────────────────────────────────────

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,        # detecta cambios de tipo en columnas
            compare_server_default=False,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
