<div align="center">

# APIPunchClock

**Sistema de control de asistencia y marcaje de empleados desarrollado con FastAPI, siguiendo una arquitectura en capas orientada a la mantenibilidad, escalabilidad y separación clara de responsabilidades.**

El proyecto permite gestionar el proceso de marcaje de entrada y salida mediante autenticación por PIN y JWT, manejo de horarios fijos y flexibles, control de tolerancias, generación de reportes diarios y exportación de información para Recursos Humanos.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-336791?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?style=flat-square)
![Alembic](https://img.shields.io/badge/Alembic-1.13+-6BA539?style=flat-square)
![JWT](https://img.shields.io/badge/Auth-JWT_HS256-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)

</div>

---

## Descripcion

APIPunchClock fue desarrollado para digitalizar el proceso de registro de asistencia de empleados, permitiendo controlar horarios laborales, validar puntualidad y generar reportes de forma precisa y eficiente.

El sistema esta orientado a organizaciones con multiples departamentos, distintos tipos de jornada y la necesidad de trazabilidad completa del historial de asistencia.

El sistema soporta:

- Marcaje de entrada y salida mediante PIN personal de 4 digitos
- Horarios fijos con tolerancia configurable en minutos por horario
- Horarios flexibles y turnos partidos (doble jornada en el mismo dia)
- Turnos nocturnos con manejo correcto del cruce de medianoche (22:00 → 06:00)
- Autenticacion segura mediante PIN con proteccion de endpoints via JWT
- Dashboard con metricas operativas en tiempo real (presentes, ausentes, tardanzas, puntualidad)
- Reportes diarios e historicos con filtros por rango de fechas de hasta 60 dias
- Exportacion de datos en formato CSV para integracion con sistemas de Recursos Humanos

---

## Tecnologias

| Capa | Tecnologia | Rol |
|---|---|---|
| API Framework | FastAPI 0.111+ | Definicion de endpoints, documentacion automatica (Swagger/ReDoc) |
| ORM | SQLAlchemy 2.0+ | Mapeo objeto-relacional, gestion de sesiones y queries |
| Base de datos | PostgreSQL 13+ | Motor relacional principal optimizado para produccion |
| Driver BD | psycopg 3.x | Adaptador PostgreSQL nativo para Python (psycopg[binary]) |
| Migraciones | Alembic 1.13+ | Control de versiones del esquema de base de datos |
| Validacion | Pydantic 2.7+ | Validacion de tipos, schemas de entrada/salida y configuracion |
| Autenticacion | Python-Jose (JWT HS256) | Generacion y verificacion de tokens de acceso |
| Servidor | Uvicorn | Servidor ASGI de alto rendimiento |
| Frontend | HTML5 · Bootstrap 5.3 · Vanilla JS | Interfaz web responsiva sin frameworks adicionales |
| Datos de prueba | Faker (es_MX) | Generacion de empleados y marcajes historicos realistas |

> El proyecto fue migrado desde SQLite a PostgreSQL para asegurar soporte optimo en entornos de produccion, aprovechando el tipo nativo UUID, indices compuestos, constraints y el manejo de zonas horarias.

## Arquitectura del sistema

APIPunchClock implementa una arquitectura en capas con dependencias estrictamente unidireccionales. Ninguna capa conoce la existencia de la capa que la invoca, garantizando bajo acoplamiento y alta cohesion.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HTTP Request / Response                     │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               ▼
╔═════════════════════════════════════════════════════════════════════╗
║             CAPA 1 — ROUTERS & SCHEMAS  (API Layer)                ║
║  app/routers/  —  auth · clock · employees · reports               ║
║  app/schemas/  —  LoginRequest · ClockRequest · EmployeeOut        ║
║                                                                     ║
║  · Punto de entrada unico para todas las solicitudes HTTP          ║
║  · Validacion automatica y rigurosa de payloads con Pydantic       ║
║  · Extraccion y verificacion del JWT mediante Depends()            ║
║  · Serializacion de respuestas a traves de schemas tipados         ║
║  · No contiene logica de negocio ni acceso directo a la BD         ║
╚══════════════════════════════╦══════════════════════════════════════╝
                               ║  invoca
                               ▼
╔═════════════════════════════════════════════════════════════════════╗
║             CAPA 2 — SERVICES  (Business Logic Layer)              ║
║  app/services/  —  clock_service · report_service                  ║
║                                                                     ║
║  · Capa aislada donde reside toda la logica de negocio pura        ║
║  · Validacion de reglas del dominio: secuencia de eventos,         ║
║    tolerancias, turno partido, cruce de medianoche nocturno        ║
║  · Calculo de estados: on_time / late / flexible                   ║
║  · Generacion de estadisticas, reportes y exportacion CSV          ║
║  · Orquesta llamadas al Repository — nunca ejecuta queries         ║
╚══════════════════════════════╦══════════════════════════════════════╝
                               ║  delega acceso a datos
                               ▼
╔═════════════════════════════════════════════════════════════════════╗
║             CAPA 3 — REPOSITORIES  (Data Access Layer)             ║
║  app/repositories/  —  employee_repo · clock_repo                  ║
║                                                                     ║
║  · Unica capa autorizada para escribir queries SQLAlchemy ORM      ║
║  · Encapsula filtros, joins, ordenamientos y eager loading         ║
║  · Implementa el Patron Repositorio para abstraer la fuente        ║
║  · Utiliza joinedload para prevenir el problema de consultas N+1   ║
║  · No aplica reglas de negocio ni lanza excepciones HTTP           ║
╚══════════════════════════════╦══════════════════════════════════════╝
                               ║  persiste y consulta
                               ▼
╔═════════════════════════════════════════════════════════════════════╗
║             CAPA 4 — MODELS & DATABASE  (Persistence Layer)        ║
║  app/models/  —  Employee · ClockRecord · Assignment · ...         ║
║                                                                     ║
║  · Definicion declarativa de entidades y relaciones (ORM)          ║
║  · Constraints, indices compuestos y UUIDs optimizados para PG     ║
║  · Esquema versionado y reproducible mediante Alembic              ║
║  · Separacion entre clock_time (normalizada) y real_time (RRHH)   ║
╚═════════════════════════════════════════════════════════════════════╝
```

> Regla de oro: las dependencias fluyen exclusivamente hacia abajo. Un Router llama a un Service. Un Service nunca importa de un Router. Un Repository nunca conoce la existencia de un Service.

---

## Estructura del proyecto

```
APIPUNCHCLOCK/
├── app/
│   ├── core/                  # Configuracion central y utilidades transversales
│   │   ├── base.py            # Base declarativa unica de SQLAlchemy
│   │   ├── config.py          # Settings via pydantic-settings + .env
│   │   ├── constants.py       # Mapas ID <-> nombre compartidos entre capas
│   │   ├── database.py        # Engine, SessionLocal y dependencia get_db
│   │   ├── security.py        # Creacion/verificacion JWT · get_current_user
│   │   └── utils.py           # Utilidades puras de tiempo (sin acceso a BD)
│   ├── database/
│   │   ├── fixtures/          # Datos de catalogo: departamentos, turnos, horarios
│   │   ├── seeders/           # Seeders de desarrollo con Faker (empleados, marcajes)
│   │   └── setup.sql          # Setup completo para PostgreSQL / Supabase
│   ├── models/                # Entidades ORM — definicion de tablas PostgreSQL
│   ├── repositories/          # Patron Repositorio — unica capa con acceso a BD
│   ├── routers/               # Controladores HTTP — endpoints de la API
│   ├── schemas/               # Pydantic — validacion de entrada y salida
│   └── services/              # Logica de negocio pura y orquestacion
├── frontend/
│   ├── css/
│   ├── js/
│   │   └── api.js             # Capa centralizada de comunicacion con la API
│   ├── index.html             # Pantalla de login (teclado PIN virtual)
│   ├── dashboard.html         # KPIs del dia y marcajes recientes
│   ├── clock.html             # Pantalla de marcaje individual
│   ├── employees.html         # Listado y horarios de empleados
│   └── reports.html           # Reportes historicos y exportacion CSV
├── migrations/
│   ├── versions/
│   │   └── 0001_initial_schema.py
│   └── env.py                 # Integrado con app.core.config y Base
├── scripts/
│   └── seed.py                # Script de automatizacion para poblado de datos
├── alembic.ini
├── main.py
├── README.md
└── requirements.txt
```

## Funcionalidades principales

### Autenticacion

El flujo de autenticacion combina la simplicidad de un PIN fisico con la seguridad de tokens JWT:

1. El empleado ingresa su PIN en el teclado virtual del navegador.
2. El servidor verifica el PIN contra la base de datos y genera un token JWT firmado (HS256) con `employee_id`, `is_admin` y `exp`.
3. El token se almacena en `sessionStorage` y se adjunta automaticamente como `Authorization: Bearer <token>` en cada solicitud.
4. La dependencia `get_current_user` verifica la firma, la expiracion y el estado activo del empleado en cada endpoint protegido.

### Gestion de empleados

- Listado de todos los empleados activos, ordenados por departamento y nombre.
- Consulta del horario asignado para cualquier fecha, con soporte para turno partido (hasta dos jornadas distintas en el mismo dia).
- Filtrado en tiempo real por departamento y busqueda por nombre, ejecutados en el cliente sin solicitudes adicionales al servidor.
- Visualizacion del tipo de horario (`fixed` / `flexible`) y tolerancia configurada de cada empleado.

### Sistema de marcaje

El motor de marcaje clasifica automaticamente cada registro de entrada:

| Estado | Condicion de evaluacion | clock_time almacenado |
|---|---|---|
| `on_time` | Hora de llegada <= check_in_time + tolerance_minutes | Hora oficial del horario (normalizada) |
| `late` | Hora de llegada supera la tolerancia permitida | Hora real del reloj |
| `flexible` | Empleado sin horario fijo asignado para ese dia | Hora real del reloj |

Reglas de integridad del flujo de marcaje:
- No se permite registrar dos entradas consecutivas sin una salida intermedia (HTTP 409).
- No se permite registrar una salida sin haber registrado una entrada previa (HTTP 409).
- El `employee_id` se extrae exclusivamente del JWT. El body de la solicitud solo acepta el tipo de evento, eliminando por diseno la posibilidad de suplantacion.

Soporte para turno nocturno (22:00 → 06:00):
- Normalizacion automatica de +1440 minutos cuando el horario comienza >= 20:00 y la hora actual es < 10:00, garantizando comparaciones correctas en el cruce de medianoche.
- El checkout en madrugada detecta automaticamente el check-in de la jornada anterior y almacena ambos registros con el mismo `work_date` para coherencia en reportes y CSV.

### Reportes y estadisticas

- **Dashboard en tiempo real:** total de empleados activos, presentes, tardanzas, ausentes y tasa de puntualidad del dia.
- **Grafico de asistencia:** barras apiladas de los ultimos 7 dias (presentes vs. tardanzas), renderizadas en el cliente sin librerias de graficacion externas.
- **Historial de registros:** tabla paginada (25 registros/pagina) con filtros por tipo de evento, estado y busqueda de texto.
- **Exportacion CSV:** generado completamente en memoria sin archivos temporales en disco, con una fila por jornada completa (entrada + salida) mediante funcion de pivoteo por `(employee_id, work_date)`.

---

## Seguridad

| Mecanismo | Implementacion tecnica |
|---|---|
| JWT Authentication | Tokens firmados con HS256 usando `python-jose`. `SECRET_KEY` configurable via `.env`. Expiracion personalizable con `ACCESS_TOKEN_EXPIRE_MINUTES`. |
| Validacion de usuarios activos | `get_current_user` verifica en cada solicitud que el `employee_id` exista en la BD y que `active = True`. Un empleado desactivado no puede operar aunque conserve un token valido. |
| Proteccion contra suplantacion | El `employee_id` nunca se acepta en el body de las solicitudes de marcaje. Se extrae exclusivamente del JWT. |
| Validacion de payloads | Todos los schemas de entrada estan definidos con Pydantic 2. Los valores invalidos son rechazados con HTTP 422 antes de llegar a la capa de servicio. |
| Proteccion XSS | Los nombres de empleados no se interpolan en atributos `onclick` del HTML. Se almacena unicamente el entero `data-emp-id` y el nombre se recupera del array en memoria. |
| Sesion | `sessionStorage` en lugar de `localStorage`. La sesion expira automaticamente al cerrar la pestana del navegador. |

---

## Instalacion y configuracion

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/APIPunchClock.git
cd APIPunchClock
```

### 2. Crear y activar el entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Editar el archivo `.env` con los valores del entorno:

```env
# Base de datos PostgreSQL (psycopg3)
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/apipunchclock

# JWT
# Generar con: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=cambia-este-valor-en-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Aplicacion
DEBUG=false
APP_TITLE=PunchClock API
APP_VERSION=2.0.0
```

### 5. Crear la base de datos en PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE apipunchclock;"
```

### 6. Ejecutar las migraciones con Alembic

```bash
python -m alembic upgrade head
```

> Si las tablas ya fueron creadas mediante `create_tables()`, marcar como aplicadas sin ejecutar los DDL:
> ```bash
> python -m alembic stamp head
> ```

### 7. Poblar con datos de prueba (solo para desarrollo)

```bash
python scripts/seed.py
python scripts/seed.py --reset    # Resetear y repoblar desde cero
```

### 8. Iniciar el servidor

```bash
# Desarrollo
uvicorn main:app --reload --port 8765

# Produccion
uvicorn main:app --host 0.0.0.0 --port 8765
```

| Recurso | URL |
|---|---|
| API Base | `http://localhost:8765` |
| Swagger UI | `http://localhost:8765/docs` |
| ReDoc | `http://localhost:8765/redoc` |
| Health Check | `http://localhost:8765/health` |
| Frontend | Abrir `frontend/index.html` en el navegador |

---

## Endpoints principales

### Autenticacion

| Metodo | Ruta | Descripcion | Auth |
|---|---|---|:---:|
| `POST` | `/auth/login` | Autentica por PIN y retorna JWT + datos del empleado | — |

### Marcaje

| Metodo | Ruta | Descripcion | Auth |
|---|---|---|:---:|
| `POST` | `/clock` | Registra entrada o salida del empleado autenticado | JWT |
| `GET` | `/clock/today` | Marcajes del dia actual, filtrable por `employee_id` | JWT |
| `GET` | `/clock/range` | Marcajes en un rango `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` | JWT |

### Empleados

| Metodo | Ruta | Descripcion | Auth |
|---|---|---|:---:|
| `GET` | `/employees` | Lista todos los empleados activos ordenados por departamento | JWT |
| `GET` | `/employees/{id}/assignment` | Horario asignado del empleado para una fecha `?work_date=` | JWT |

### Reportes

| Metodo | Ruta | Descripcion | Auth |
|---|---|---|:---:|
| `GET` | `/stats/today` | KPIs del dia: presentes, ausentes, tardanzas, puntualidad | JWT |
| `GET` | `/reports/daily` | Resumen diario para los ultimos N dias `?days=7` (max. 60) | JWT |
| `GET` | `/export/csv` | Descarga CSV del historial `?since=YYYY-MM-DD&until=YYYY-MM-DD` | JWT |

### Sistema

| Metodo | Ruta | Descripcion | Auth |
|---|---|---|:---:|
| `GET` | `/health` | Verificacion de disponibilidad del servidor | — |

---

## Migraciones con Alembic

```bash
# Estado actual de la base de datos
python -m alembic current

# Historial completo de revisiones
python -m alembic history

# Generar nueva migracion a partir de cambios en los modelos
python -m alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar todas las migraciones pendientes
python -m alembic upgrade head

# Revertir la ultima migracion aplicada
python -m alembic downgrade -1

# Previsualizar el SQL que se ejecutaria sin aplicar cambios
python -m alembic upgrade head --sql
```

---

## Requisitos del sistema

| Requisito | Version minima |
|---|---|
| Python | 3.11+ |
| PostgreSQL | 13+ |
| pip | 23+ |

> Node.js no es requerido. El frontend esta implementado en HTML, CSS y JavaScript puro.

---

## Autor

**Henry Birminghan**

[![GitHub](https://img.shields.io/badge/GitHub-birminghanhenryarch-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/birminghanhenryarch)

---

<sub>Desarrollado con FastAPI · PostgreSQL · SQLAlchemy · Alembic · Bootstrap 5</sub>
