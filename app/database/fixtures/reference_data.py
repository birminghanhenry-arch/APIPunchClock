"""
database/fixtures/reference_data.py
Datos de referencia inmutables del sistema.
Estos valores NO cambian entre entornos (dev/staging/prod).

Son las "tablas catálogo": departamentos, turnos, horarios,
tipos de evento y estados de marcaje.
"""
from datetime import time

# ── Departamentos ─────────────────────────────────────────────────────────────
DEPARTMENTS: list[tuple[int, str]] = [
    (1,  "Cocina"),
    (2,  "Panadería"),
    (3,  "Salón"),
    (4,  "Bodega"),
    (5,  "Seguridad"),
    (6,  "Contabilidad"),
    (7,  "Lavandería"),
    (8,  "Taller"),
    (9,  "Oficina"),
    (10, "Mantenimiento"),
]

# ── Turnos ────────────────────────────────────────────────────────────────────
SHIFTS: list[tuple[int, str]] = [
    (1, "Mañana"),
    (2, "Tarde"),
    (3, "Noche"),
]

# ── Horarios ──────────────────────────────────────────────────────────────────
# (id, shift_id, hora_entrada, hora_salida, tolerancia_minutos)
SCHEDULES: list[tuple[int, int, time, time, int]] = [
    (1,  1, time(6,  0),  time(14,  0), 10),  # Mañana temprano
    (2,  1, time(7,  0),  time(15,  0), 10),  # Mañana estándar
    (3,  1, time(8,  0),  time(16,  0), 10),  # Mañana administrativa
    (4,  1, time(9,  0),  time(17,  0), 10),  # Mañana tarde
    (5,  1, time(10, 30), time(14, 30), 10),  # Media mañana J1
    (6,  1, time(11,  0), time(15,  0), 10),  # Media mañana J1 extendida
    (7,  1, time(12,  0), time(16,  0), 10),  # Mediodía J1
    (8,  2, time(15,  0), time(23,  0), 10),  # Tarde completa
    (9,  2, time(17, 30), time(22,  0), 10),  # Tarde J2
    (10, 2, time(18,  0), time(22, 30), 10),  # Tarde J2 extendida
    (11, 3, time(22,  0), time(6,   0), 10),  # Noche
]

# ── Tipos de evento de marcaje ────────────────────────────────────────────────
CLOCK_EVENT_TYPES: list[tuple[int, str]] = [
    (1, "check_in"),
    (2, "check_out"),
]

# ── Estados de marcaje ────────────────────────────────────────────────────────
CLOCK_STATUSES: list[tuple[int, str]] = [
    (1, "on_time"),   # Llegó dentro de la tolerancia
    (2, "late"),      # Llegó después de la tolerancia
    (3, "flexible"),  # Empleado sin horario fijo asignado
]

# ── Mapa departamento → horarios ──────────────────────────────────────────────
# (horarios_primarios, horarios_secundarios)
# horarios_secundarios = None  → jornada simple
# horarios_secundarios = [ids] → doble jornada (turno partido)
DEPT_SCHEDULE_MAP: dict[int, tuple[list[int], list[int] | None]] = {
    1:  ([5, 6], [9]),       # Cocina: split shifts
    2:  ([1],    None),      # Panadería: mañana temprano
    3:  ([6, 7], [9, 10]),   # Salón: split shifts
    4:  ([2],    None),      # Bodega
    5:  ([8],    None),      # Seguridad (tarde, flexible)
    6:  ([3],    None),      # Contabilidad (flexible)
    7:  ([1],    None),      # Lavandería
    8:  ([2],    None),      # Taller
    9:  ([3],    None),      # Oficina
    10: ([3],    None),      # Mantenimiento
}
