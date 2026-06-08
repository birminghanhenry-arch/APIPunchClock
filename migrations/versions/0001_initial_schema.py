"""initial_schema

Revision ID: 0001
Revises:
Create Date: 2026-06-08

Representa el estado inicial completo de APIPunchClock.
Generada manualmente a partir de los modelos SQLAlchemy.
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa

# ── Identificadores de revisión ───────────────────────────────────────────────
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    # ── 1. Tablas de catálogo (sin FK) ────────────────────────────────────────

    op.create_table(
        "departments",
        sa.Column("id",   sa.Integer(),     nullable=False),
        sa.Column("name", sa.String(80),    nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "shifts",
        sa.Column("id",   sa.Integer(),     nullable=False),
        sa.Column("name", sa.String(40),    nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "clock_event_types",
        sa.Column("id",   sa.Integer(),     nullable=False),
        sa.Column("name", sa.String(20),    nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "clock_statuses",
        sa.Column("id",   sa.Integer(),     nullable=False),
        sa.Column("name", sa.String(20),    nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 2. Horarios (→ shifts) ────────────────────────────────────────────────

    op.create_table(
        "schedules",
        sa.Column("id",                sa.Integer(),  nullable=False),
        sa.Column("shift_id",          sa.Integer(),  nullable=False),
        sa.Column("check_in_time",     sa.Time(),     nullable=False),
        sa.Column("check_out_time",    sa.Time(),     nullable=False),
        sa.Column("tolerance_minutes", sa.Integer(),  nullable=False),
        sa.ForeignKeyConstraint(["shift_id"], ["shifts.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 3. Empleados (→ departments) ──────────────────────────────────────────

    op.create_table(
        "employees",
        sa.Column("id",                sa.Integer(),    nullable=False),
        sa.Column("full_name",         sa.String(100),  nullable=False),
        sa.Column("department_id",     sa.Integer(),    nullable=False),
        sa.Column("pin",               sa.String(10),   nullable=False),
        sa.Column("schedule_type",     sa.String(10),   nullable=False),
        sa.Column("tolerance_minutes", sa.Integer(),    nullable=False),
        sa.Column("is_admin",          sa.Boolean(),    nullable=False),
        sa.Column("active",            sa.Boolean(),    nullable=False),
        sa.CheckConstraint(
            "schedule_type IN ('fixed', 'flexible')",
            name="ck_schedule_type",
        ),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pin"),
    )

    # ── 4. Asignaciones (→ employees, schedules) ──────────────────────────────

    op.create_table(
        "assignments",
        sa.Column("id",          sa.String(36),  nullable=False),
        sa.Column("employee_id", sa.Integer(),   nullable=False),
        sa.Column("schedule_id", sa.Integer(),   nullable=False),
        sa.Column("work_date",   sa.Date(),      nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "employee_id", "schedule_id", "work_date",
            name="uq_assignment",
        ),
    )

    # ── 5. Marcajes (→ employees, clock_event_types, clock_statuses) ──────────

    op.create_table(
        "clock_records",
        sa.Column("id",          sa.String(36),   nullable=False),
        sa.Column("employee_id", sa.Integer(),    nullable=False),
        sa.Column("event_type",  sa.Integer(),    nullable=False),
        sa.Column("status",      sa.Integer(),    nullable=False),
        sa.Column("work_date",   sa.Date(),       nullable=False),
        sa.Column("clock_time",  sa.Time(),       nullable=False),
        sa.Column("real_time",   sa.Time(),       nullable=False),
        sa.Column("created_at",  sa.DateTime(),   nullable=False),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["event_type"],  ["clock_event_types.id"]),
        sa.ForeignKeyConstraint(["status"],      ["clock_statuses.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # ── 6. Índices de rendimiento ─────────────────────────────────────────────

    op.create_index(
        "idx_clock_employee_date",
        "clock_records",
        ["employee_id", "work_date"],
    )
    op.create_index(
        "idx_clock_date",
        "clock_records",
        ["work_date"],
    )
    op.create_index(
        "idx_assignment_employee_date",
        "assignments",
        ["employee_id", "work_date"],
    )
    op.create_index(
        "idx_employee_dept_active",
        "employees",
        ["department_id", "active"],
    )


def downgrade() -> None:
    # Eliminar en orden inverso (respeta FKs)
    op.drop_index("idx_employee_dept_active",      table_name="employees")
    op.drop_index("idx_assignment_employee_date",  table_name="assignments")
    op.drop_index("idx_clock_date",                table_name="clock_records")
    op.drop_index("idx_clock_employee_date",       table_name="clock_records")

    op.drop_table("clock_records")
    op.drop_table("assignments")
    op.drop_table("employees")
    op.drop_table("schedules")
    op.drop_table("clock_event_types")
    op.drop_table("clock_statuses")
    op.drop_table("shifts")
    op.drop_table("departments")
