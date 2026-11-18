// Funciones comunes de la interfaz: conexión con la API, sesión y menú según el rol.

const ETIQUETAS_ROL = {
  PARTICIPANTE: "Participante",
  ORGANIZADOR: "Organizador",
  COORDINACION: "Coordinación",
};

// Nombre e ícono de cada tipo de actividad (se usan en tarjetas, tablas y fichas).
const TIPOS = {
  CONFERENCIA: { nombre: "Conferencia", icono: "🎤" },
  TALLER: { nombre: "Taller", icono: "🛠️" },
  SEMINARIO: { nombre: "Seminario", icono: "📚" },
  CAPACITACION: { nombre: "Capacitación", icono: "🩺" },
};

const ETIQUETAS_ESTADO = {
  BORRADOR: "Borrador",
  PUBLICADO: "Publicado",
  CANCELADO: "Cancelado",
  ACTIVA: "Activa",
  CANCELADA: "Cancelada",
  ASISTIO: "Asistió",
  NO_ASISTIO: "No asistió",
};

function obtenerUsuario() {
  try {
    return JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

function guardarSesion(token, usuario) {
  localStorage.setItem("token", token);
  localStorage.setItem("usuario", JSON.stringify(usuario));
}

function borrarSesion() {
  localStorage.removeItem("token");
  localStorage.removeItem("usuario");
}

// Llama a la API REST y devuelve los datos de la respuesta o lanza un error con mensaje claro.
async function api(ruta, { metodo = "GET", datos } = {}) {
  // "no-store": siempre se piden datos frescos (los cupos cambian en todo momento).
  const opciones = { method: metodo, headers: {}, cache: "no-store" };
  const token = localStorage.getItem("token");
  if (token) opciones.headers["Authorization"] = `Bearer ${token}`;
  if (datos !== undefined) {
    opciones.headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(datos);
  }
  let respuesta;
  try {
    respuesta = await fetch(ruta, opciones);
  } catch {
    throw new Error("No hay conexión con el servidor.");
  }
  if (respuesta.status === 204) return null;
  const cuerpo = await respuesta.json().catch(() => ({}));
  if (!respuesta.ok) {
    if (respuesta.status === 401 && token) {
      borrarSesion(); // la sesión venció
    }
    let mensaje = cuerpo.detail || `Error ${respuesta.status}`;
    if (Array.isArray(cuerpo.errores)) mensaje += ": " + cuerpo.errores.join(" | ");
    const error = new Error(mensaje);
    error.codigo = respuesta.status;
    throw error;
  }
  return cuerpo;
}

function mostrarMensaje(texto, tipo = "exito") {
  const caja = document.getElementById("mensaje");
  if (!caja) return alert(texto);
  caja.textContent = texto;
  caja.className = `mensaje ${tipo}`;
  caja.hidden = false;
  caja.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function ocultarMensaje() {
  const caja = document.getElementById("mensaje");
  if (caja) caja.hidden = true;
}

// Redirige al login si la persona no tiene alguno de los roles requeridos.
function exigirRol(...roles) {
  const usuario = obtenerUsuario();
  if (!usuario || !roles.includes(usuario.rol)) {
    window.location.href = "login.html?volver=" + encodeURIComponent(location.pathname + location.search);
    throw new Error("Acceso no autorizado");
  }
  return usuario;
}

async function cerrarSesion() {
  try {
    await api("/api/auth/logout", { metodo: "POST" });
  } catch {
    /* si ya venció, igual se borra localmente */
  }
  borrarSesion();
  window.location.href = "index.html";
}

// Menú superior: muestra solo las opciones que corresponden al rol.
function construirMenu() {
  const usuario = obtenerUsuario();
  const enlaces = [["index.html", "📅 Catálogo"]];
  if (usuario?.rol === "PARTICIPANTE") enlaces.push(["mis-inscripciones.html", "🎟️ Mis inscripciones"]);
  if (usuario?.rol === "ORGANIZADOR" || usuario?.rol === "COORDINACION") enlaces.push(["gestion.html", "🗂️ Gestión de eventos"]);
  if (usuario?.rol === "COORDINACION") enlaces.push(["reportes.html", "📊 Reportes"]);

  let pagina = location.pathname.split("/").pop() || "index.html";
  if (pagina === "asistencia.html") pagina = "gestion.html";
  const nav = document.getElementById("menu");
  nav.innerHTML = `
    <a class="marca" href="index.html"><span class="logo">🎓</span> Eventos Académicos</a>
    <div class="enlaces">
      ${enlaces.map(([href, texto]) => `<a href="${href}" class="${pagina === href ? "activo" : ""}">${texto}</a>`).join("")}
    </div>
    <div class="usuario">
      ${
        usuario
          ? `<div class="persona">
               <span class="avatar">${iniciales(usuario.nombre)}</span>
               <div><span>${escapar(usuario.nombre)}</span><small>${ETIQUETAS_ROL[usuario.rol]}</small></div>
             </div>
             <button class="salir" onclick="cerrarSesion()">Cerrar sesión</button>`
          : `<a class="boton-blanco" href="login.html">Iniciar sesión</a>`
      }
    </div>`;

  if (!document.querySelector("footer.pie")) {
    document.body.insertAdjacentHTML(
      "beforeend",
      `<footer class="pie">🎓 Eventos Académicos · Organización de eventos y actividades académicas de la institución</footer>`
    );
  }
}

// Ícono de la pestaña del navegador (evita además el error 404 de favicon.ico).
function ponerIcono() {
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎓</text></svg>`;
  document.head.insertAdjacentHTML("beforeend", `<link rel="icon" href="data:image/svg+xml,${encodeURIComponent(svg)}">`);
}
ponerIcono();

// ---- Utilidades de formato ----
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

function formatoFecha(iso) {
  if (!iso) return "";
  const [a, m, d] = iso.slice(0, 10).split("-");
  return `${d}/${m}/${a}`;
}

const MESES = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"];

// Devuelve { dia: "19", mes: "NOV" } para dibujar el bloque de fecha.
function partesFecha(iso) {
  const [, m, d] = (iso || "").slice(0, 10).split("-");
  return { dia: d || "", mes: MESES[Number(m) - 1] || "" };
}

// Fecha de hoy en formato AAAA-MM-DD (hora local).
function hoyIso() {
  const h = new Date();
  return `${h.getFullYear()}-${String(h.getMonth() + 1).padStart(2, "0")}-${String(h.getDate()).padStart(2, "0")}`;
}

function iniciales(nombre) {
  return (nombre || "?").split(/\s+/).filter(Boolean).slice(0, 2).map((p) => p[0].toUpperCase()).join("");
}

function nombreTipo(tipo) {
  const t = TIPOS[tipo];
  return t ? `${t.icono} ${t.nombre}` : tipo;
}

// Clase de color de la barra de cupos según qué tan llena está.
function nivelOcupacion(inscritos, cupo) {
  const p = cupo ? inscritos / cupo : 0;
  if (p >= 1) return "lleno";
  if (p >= 0.8) return "alto";
  if (p >= 0.5) return "medio";
  return "";
}

function formatoHora(hora) {
  return hora ? hora.slice(0, 5) : "";
}

function etiquetaEstado(estado) {
  const clase = estado ? estado.toLowerCase() : "sin";
  return `<span class="estado estado-${clase}">${ETIQUETAS_ESTADO[estado] || estado || "Sin registro"}</span>`;
}

document.addEventListener("DOMContentLoaded", construirMenu);
