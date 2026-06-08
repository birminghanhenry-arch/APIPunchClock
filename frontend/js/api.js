/**
 * api.js — Capa centralizada de comunicación con APIPunchClock API
 *
 * Configuración:
 *   Sin cambios de código para desplegar. Opciones en orden de prioridad:
 *
 *   1. window.APP_CONFIG.apiUrl  → define antes de cargar este script:
 *        <script>window.APP_CONFIG = { apiUrl: "https://api.ejemplo.com" };</script>
 *
 *   2. window.location.origin   → default: misma origen que el HTML.
 *        Funciona en dev (uvicorn sirve el frontend) y en reverse proxy.
 */
const BASE_URL = window.APP_CONFIG?.apiUrl ?? window.location.origin;

// ── Sesión ────────────────────────────────────────────────────────────────────
// Login devuelve { access_token, token_type, employee }.
// Guardamos token y employee por separado en sessionStorage.

const Session = {
  save(loginResponse) {
    sessionStorage.setItem("token",    loginResponse.access_token);
    sessionStorage.setItem("employee", JSON.stringify(loginResponse.employee));
  },
  get() {
    const raw = sessionStorage.getItem("employee");
    return raw ? JSON.parse(raw) : null;
  },
  getToken() {
    return sessionStorage.getItem("token");
  },
  clear() {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("employee");
  },
  isAdmin() {
    return this.get()?.is_admin ?? false;
  },
  requireAuth() {
    if (!this.get() || !this.getToken()) {
      window.location.href = "/frontend/index.html";
    }
  },
};

// ── Cliente HTTP base ─────────────────────────────────────────────────────────

async function request(method, path, body = null) {
  const opts = {
    method,
    headers: { "Content-Type": "application/json" },
  };

  const token = Session.getToken();
  if (token) opts.headers["Authorization"] = `Bearer ${token}`;

  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(BASE_URL + path, opts);

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Error de servidor" }));
    throw new ApiError(res.status, err.detail || "Error desconocido");
  }

  // Algunos endpoints retornan archivo (CSV) — devolver la respuesta raw
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("text/csv")) return res;

  return res.json();
}

class ApiError extends Error {
  constructor(status, detail) {
    super(detail);
    this.status  = status;
    this.detail  = detail;
  }
}

// ── Endpoints ─────────────────────────────────────────────────────────────────

const Api = {
  // Auth
  login: (pin) =>
    request("POST", "/auth/login", { pin }),

  // Employees
  listEmployees: () =>
    request("GET", "/employees"),

  getAssignment: (employeeId, date = null) => {
    const qs = date ? `?work_date=${date}` : "";
    return request("GET", `/employees/${employeeId}/assignment${qs}`);
  },

  // Clock
  clockEvent: (eventType) =>
    request("POST", "/clock", { event_type: eventType }),

  clockToday: (employeeId = null) => {
    const qs = employeeId ? `?employee_id=${employeeId}` : "";
    return request("GET", `/clock/today${qs}`);
  },

  clockRange: (startDate, endDate) => {
    const params = new URLSearchParams({ start_date: startDate, end_date: endDate });
    return request("GET", `/clock/range?${params}`);
  },

  // Reports
  statsToday: () =>
    request("GET", "/stats/today"),

  dailyReport: (days = 7) =>
    request("GET", `/reports/daily?days=${days}`),

  exportCsv: (since = null, until = null) => {
    const params = new URLSearchParams();
    if (since) params.append("since", since);
    if (until) params.append("until", until);
    const qs = params.toString() ? "?" + params.toString() : "";
    return request("GET", `/export/csv${qs}`);
  },

  // System
  health: () =>
    request("GET", "/health"),
};

// ── Helpers UI ────────────────────────────────────────────────────────────────

/**
 * Muestra un alert de Bootstrap en el contenedor indicado.
 * type: 'success' | 'danger' | 'warning' | 'info'
 */
function showAlert(containerId, message, type = "danger", autoDismiss = 4000) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const id = "alert-" + Date.now();
  container.innerHTML = `
    <div id="${id}" class="alert alert-${type} alert-dismissible fade show" role="alert">
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    </div>`;

  if (autoDismiss) {
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) el.classList.remove("show");
    }, autoDismiss);
  }
}

/**
 * Muestra/oculta un spinner dentro de un botón mientras dura la operación.
 */
function withLoading(btn, asyncFn) {
  const original = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Cargando…`;
  return asyncFn().finally(() => {
    btn.disabled  = false;
    btn.innerHTML = original;
  });
}

/**
 * Formatea "FULANO DE TAL" → "Fulano De Tal"
 */
function titleCase(str) {
  return str.replace(/\w\S*/g, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase());
}

/**
 * Retorna badge HTML según el estado del marcaje.
 */
function statusBadge(status) {
  const map = {
    on_time:  ["success", "A tiempo"],
    late:     ["warning", "Tardanza"],
    flexible: ["info",    "Flexible"],
  };
  const [color, label] = map[status] || ["secondary", status];
  return `<span class="badge text-bg-${color}">${label}</span>`;
}

/**
 * Retorna badge HTML para tipo de evento.
 */
function eventBadge(eventType) {
  return eventType === "check_in"
    ? `<span class="badge text-bg-primary">Entrada</span>`
    : `<span class="badge text-bg-secondary">Salida</span>`;
}

/**
 * Formatea HH:MM:SS → HH:MM
 */
function fmtTime(t) {
  return t ? t.slice(0, 5) : "—";
}

/**
 * Rellena el nombre del usuario en el navbar si existe #navbar-user
 */
function renderNavUser() {
  const emp = Session.get();
  if (!emp) return;
  const el = document.getElementById("navbar-user");
  if (el) el.textContent = titleCase(emp.full_name);
  const deptEl = document.getElementById("navbar-dept");
  if (deptEl) deptEl.textContent = emp.department;
  // Mostrar items de admin
  if (emp.is_admin) {
    document.querySelectorAll(".admin-only").forEach((el) => el.classList.remove("d-none"));
  }
}

/**
 * Logout global — limpiar sesión y redirigir
 */
function logout() {
  Session.clear();
  window.location.href = "/frontend/index.html";
}
