-- ============================================================
-- APIPunchClock — Setup completo para PostgreSQL
-- ============================================================
-- Ejecutar en orden. Compatible con PostgreSQL 13+
-- Supabase: pegar directo en SQL Editor
-- psql: psql -U usuario -d base_de_datos -f setup.sql
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 1 — LIMPIEZA (opcional, solo en desarrollo)
-- Descomenta si quieres borrar todo y empezar desde cero
-- ════════════════════════════════════════════════════════════

-- DROP TABLE IF EXISTS clock_records  CASCADE;
-- DROP TABLE IF EXISTS assignments     CASCADE;
-- DROP TABLE IF EXISTS employees       CASCADE;
-- DROP TABLE IF EXISTS schedules       CASCADE;
-- DROP TABLE IF EXISTS shifts          CASCADE;
-- DROP TABLE IF EXISTS departments     CASCADE;
-- DROP TABLE IF EXISTS clock_event_types CASCADE;
-- DROP TABLE IF EXISTS clock_statuses  CASCADE;


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 2 — TABLAS
-- ════════════════════════════════════════════════════════════

-- ── 1. Departamentos ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS departments (
    id   INTEGER PRIMARY KEY,
    name VARCHAR(80) NOT NULL
);

-- ── 2. Turnos ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS shifts (
    id   INTEGER PRIMARY KEY,
    name VARCHAR(40) NOT NULL        -- 'Mañana' | 'Tarde' | 'Noche'
);

-- ── 3. Tipos de evento ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS clock_event_types (
    id   INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL        -- 'check_in' | 'check_out'
);

-- ── 4. Estados de marcaje ────────────────────────────────────
CREATE TABLE IF NOT EXISTS clock_statuses (
    id   INTEGER PRIMARY KEY,
    name VARCHAR(20) NOT NULL        -- 'on_time' | 'late' | 'flexible'
);

-- ── 5. Horarios ──────────────────────────────────────────────
-- Un turno puede tener varios horarios concretos.
-- tolerance_minutes: minutos de gracia antes de marcar tardanza.
CREATE TABLE IF NOT EXISTS schedules (
    id                INTEGER PRIMARY KEY,
    shift_id          INTEGER NOT NULL REFERENCES shifts(id),
    check_in_time     TIME    NOT NULL,
    check_out_time    TIME    NOT NULL,
    tolerance_minutes INTEGER NOT NULL DEFAULT 10
);

-- ── 6. Empleados ─────────────────────────────────────────────
-- schedule_type:
--   'fixed'    → tiene asignación diaria; la tardanza se calcula contra el horario
--   'flexible' → sin asignación fija; sus marcajes siempre quedan como 'flexible'
-- tolerance_minutes solo aplica cuando schedule_type = 'flexible'
CREATE TABLE IF NOT EXISTS employees (
    id                INTEGER     PRIMARY KEY,
    full_name         VARCHAR(100) NOT NULL,
    department_id     INTEGER     NOT NULL REFERENCES departments(id),
    pin               VARCHAR(10) NOT NULL UNIQUE,
    schedule_type     VARCHAR(10) NOT NULL DEFAULT 'fixed'
                          CHECK (schedule_type IN ('fixed', 'flexible')),
    tolerance_minutes INTEGER     NOT NULL DEFAULT 10,
    is_admin          BOOLEAN     NOT NULL DEFAULT false,
    active            BOOLEAN     NOT NULL DEFAULT true
);

-- ── 7. Asignaciones ──────────────────────────────────────────
-- Une empleado + horario + fecha de trabajo.
-- Doble jornada (turno partido): dos filas por empleado/fecha
-- con schedule_id distinto → el UNIQUE incluye schedule_id.
CREATE TABLE IF NOT EXISTS assignments (
    id          UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    schedule_id INTEGER NOT NULL REFERENCES schedules(id),
    work_date   DATE    NOT NULL,
    CONSTRAINT uq_assignment UNIQUE (employee_id, schedule_id, work_date)
);

-- ── 8. Marcajes ───────────────────────────────────────────────
-- clock_time → hora normalizada (= hora del horario si llegó a tiempo)
-- real_time  → hora real del reloj (la que aparece en reportes de RRHH)
CREATE TABLE IF NOT EXISTS clock_records (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    employee_id INTEGER     NOT NULL REFERENCES employees(id),
    event_type  INTEGER     NOT NULL REFERENCES clock_event_types(id),
    status      INTEGER     NOT NULL REFERENCES clock_statuses(id),
    work_date   DATE        NOT NULL,
    clock_time  TIME        NOT NULL,
    real_time   TIME        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 3 — ÍNDICES
-- Mejoran el rendimiento de las consultas más frecuentes
-- ════════════════════════════════════════════════════════════

-- Buscar todos los marcajes de un empleado en una fecha (pantalla principal)
CREATE INDEX IF NOT EXISTS idx_clock_employee_date
    ON clock_records (employee_id, work_date);

-- Buscar todos los marcajes de un día (vista admin "Todos hoy")
CREATE INDEX IF NOT EXISTS idx_clock_date
    ON clock_records (work_date);

-- Buscar asignaciones de un empleado para una fecha
CREATE INDEX IF NOT EXISTS idx_assignment_employee_date
    ON assignments (employee_id, work_date);

-- Filtrar empleados activos por departamento
CREATE INDEX IF NOT EXISTS idx_employee_dept_active
    ON employees (department_id, active);


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 4 — DATOS DE REFERENCIA (catálogos)
-- Valores fijos del sistema. No modificar en producción.
-- ════════════════════════════════════════════════════════════

-- Departamentos
INSERT INTO departments (id, name) VALUES
    (1,  'Cocina'),
    (2,  'Panadería'),
    (3,  'Salón'),
    (4,  'Bodega'),
    (5,  'Seguridad'),
    (6,  'Contabilidad'),
    (7,  'Lavandería'),
    (8,  'Taller'),
    (9,  'Oficina'),
    (10, 'Mantenimiento')
ON CONFLICT (id) DO NOTHING;

-- Turnos
INSERT INTO shifts (id, name) VALUES
    (1, 'Mañana'),
    (2, 'Tarde'),
    (3, 'Noche')
ON CONFLICT (id) DO NOTHING;

-- Tipos de evento
INSERT INTO clock_event_types (id, name) VALUES
    (1, 'check_in'),
    (2, 'check_out')
ON CONFLICT (id) DO NOTHING;

-- Estados de marcaje
INSERT INTO clock_statuses (id, name) VALUES
    (1, 'on_time'),
    (2, 'late'),
    (3, 'flexible')
ON CONFLICT (id) DO NOTHING;

-- Horarios
-- Jornada única mañana
INSERT INTO schedules (id, shift_id, check_in_time, check_out_time, tolerance_minutes) VALUES
    (1,  1, '06:00', '14:00', 10),   -- Mañana temprano   (Lavandería, Taller, Panadería)
    (2,  1, '07:00', '15:00', 10),   -- Mañana estándar   (Bodega, Chocolatería)
    (3,  1, '08:00', '16:00', 10),   -- Administrativa    (Oficina, Mantenimiento)
    (4,  1, '09:00', '17:00', 10),   -- Mañana tarde      (referencia)
    (5,  1, '10:30', '14:30', 10),   -- Media mañana J1   (Cocina grupo A)
    (6,  1, '11:00', '15:00', 10),   -- Media mañana J1   (Cocina grupo B / Salón)
    (7,  1, '12:00', '16:00', 10),   -- Mediodía J1       (Salón)
    -- Tarde / Noche
    (8,  2, '15:00', '23:00', 10),   -- Tarde completa    (Seguridad)
    (9,  2, '17:30', '22:00', 10),   -- Tarde J2          (Cocina / Salón reingreso)
    (10, 2, '18:00', '22:30', 10),   -- Tarde J2 ext.     (Salón reingreso)
    (11, 3, '22:00', '06:00', 10)    -- Noche             (Seguridad nocturna)
ON CONFLICT (id) DO NOTHING;


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 5 — VERIFICACIÓN
-- Ejecuta estas queries para confirmar que todo quedó bien
-- ════════════════════════════════════════════════════════════

SELECT 'departments'      AS tabla, COUNT(*) AS total FROM departments
UNION ALL
SELECT 'shifts',                                COUNT(*) FROM shifts
UNION ALL
SELECT 'schedules',                             COUNT(*) FROM schedules
UNION ALL
SELECT 'clock_event_types',                     COUNT(*) FROM clock_event_types
UNION ALL
SELECT 'clock_statuses',                        COUNT(*) FROM clock_statuses
UNION ALL
SELECT 'employees',                             COUNT(*) FROM employees
UNION ALL
SELECT 'assignments',                           COUNT(*) FROM assignments
UNION ALL
SELECT 'clock_records',                         COUNT(*) FROM clock_records;

-- Resultado esperado después de solo este script (sin empleados aún):
-- departments       → 10
-- shifts            → 3
-- schedules         → 11
-- clock_event_types → 2
-- clock_statuses    → 3
-- employees         → 0  (se cargan desde el panel admin o seed de dev)
-- assignments       → 0
-- clock_records     → 0


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 6 — VISTAS ÚTILES (opcionales)
-- ════════════════════════════════════════════════════════════

-- Vista: marcajes del día con nombre de empleado
CREATE OR REPLACE VIEW v_clock_today AS
SELECT
    cr.id,
    e.full_name                     AS employee,
    d.name                          AS department,
    et.name                         AS event_type,
    cs.name                         AS status,
    cr.work_date,
    cr.real_time,
    cr.clock_time,
    cr.created_at
FROM clock_records cr
JOIN employees         e  ON e.id  = cr.employee_id
JOIN departments       d  ON d.id  = e.department_id
JOIN clock_event_types et ON et.id = cr.event_type
JOIN clock_statuses    cs ON cs.id = cr.status
WHERE cr.work_date = CURRENT_DATE
ORDER BY cr.created_at DESC;

-- Vista: resumen de asistencia del día
CREATE OR REPLACE VIEW v_attendance_summary AS
SELECT
    d.name                                      AS department,
    COUNT(DISTINCT e.id)                        AS total_employees,
    COUNT(DISTINCT cr.employee_id)              AS present,
    COUNT(DISTINCT e.id) - COUNT(DISTINCT cr.employee_id) AS absent,
    COUNT(DISTINCT cr.employee_id)
        FILTER (WHERE cr.status = 2)            AS late
FROM employees e
JOIN departments d ON d.id = e.department_id
LEFT JOIN clock_records cr
    ON cr.employee_id = e.id
    AND cr.work_date  = CURRENT_DATE
    AND cr.event_type = 1
WHERE e.active = true
GROUP BY d.name
ORDER BY d.name;

-- Vista: doble jornada — muestra las dos jornadas de cada empleado
CREATE OR REPLACE VIEW v_split_shifts AS
SELECT
    e.full_name                     AS employee,
    d.name                          AS department,
    a.work_date,
    MIN(s.check_in_time)            AS jornada1_entrada,
    MAX(s.check_in_time)            AS jornada2_entrada
FROM assignments a
JOIN employees  e ON e.id = a.employee_id
JOIN departments d ON d.id = e.department_id
JOIN schedules  s ON s.id = a.schedule_id
GROUP BY e.full_name, d.name, a.work_date
HAVING COUNT(*) > 1
ORDER BY a.work_date DESC, d.name;


-- ════════════════════════════════════════════════════════════
-- SECCIÓN 7 — ROW LEVEL SECURITY (si usas Supabase)
-- Descomenta y ajusta según tu esquema de autenticación
-- ════════════════════════════════════════════════════════════

-- ALTER TABLE employees     ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE clock_records ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE assignments   ENABLE ROW LEVEL SECURITY;

-- Política ejemplo: cada empleado solo ve sus propios marcajes
-- CREATE POLICY "empleado_ve_sus_marcajes"
--     ON clock_records FOR SELECT
--     USING (employee_id = current_setting('app.current_employee_id')::int);


-- ════════════════════════════════════════════════════════════
-- FIN DEL SCRIPT
-- ════════════════════════════════════════════════════════════
