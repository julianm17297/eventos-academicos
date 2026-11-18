"""Ejecución reproducible de las pruebas funcionales de la API.

Requisitos previos (ver docs/pruebas.md):
  1. Reiniciar la base de datos con datos de ejemplo:   cd backend  ->  python -m app.seed
  2. Iniciar el servidor:                              python -m uvicorn app.main:app
  3. En otra terminal, desde la raíz del proyecto:     python pruebas/ejecutar_pruebas.py

Cada prueba envía solicitudes HTTP reales a la API, compara el código de respuesta
obtenido con el esperado y guarda la evidencia (método, ruta, código y respuesta) en
evidencias/resultados_pruebas_api.md.

Solo usa la librería estándar de Python (no requiere instalar nada adicional).
"""
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
CLAVE = "Clave123*"
DOMINIO = "institucion.edu.co"
SALIDA = Path(__file__).resolve().parents[1] / "evidencias" / "resultados_pruebas_api.md"

resultados = []
tokens = {}


def solicitud(metodo, ruta, datos=None, usuario=None):
    encabezados = {"Content-Type": "application/json"}
    if usuario:
        encabezados["Authorization"] = f"Bearer {tokens[usuario]}"
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    req = urllib.request.Request(BASE + ruta, data=cuerpo, method=metodo, headers=encabezados)
    try:
        with urllib.request.urlopen(req) as r:
            codigo, texto = r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        codigo, texto = e.code, e.read().decode()
    try:
        respuesta = json.loads(texto) if texto else None
    except json.JSONDecodeError:
        respuesta = texto
    return codigo, respuesta


def login(usuario):
    codigo, r = solicitud("POST", "/api/auth/login", {"correo": f"{usuario}@{DOMINIO}", "clave": CLAVE})
    assert codigo == 200, f"No se pudo iniciar sesión como {usuario}: {r}"
    tokens[usuario] = r["token"]


class Prueba:
    def __init__(self, ident, nombre, requisito, condiciones, esperado):
        self.ident, self.nombre, self.requisito = ident, nombre, requisito
        self.condiciones, self.esperado = condiciones, esperado
        self.pasos, self.ok = [], True
        self.obtenido = []

    def paso(self, descripcion, metodo, ruta, codigo_esperado, datos=None, usuario=None, verificar=None):
        codigo, respuesta = solicitud(metodo, ruta, datos, usuario)
        correcto = codigo == codigo_esperado
        detalle = ""
        if correcto and verificar:
            correcto, detalle = verificar(respuesta)
        self.ok &= correcto
        self.pasos.append(
            {
                "descripcion": descripcion,
                "metodo": metodo,
                "ruta": ruta,
                "usuario": usuario or "(sin sesión)",
                "datos": datos,
                "esperado": codigo_esperado,
                "codigo": codigo,
                "respuesta": respuesta,
                "correcto": correcto,
                "detalle": detalle,
            }
        )
        return respuesta

    def nota(self, texto, correcto=True):
        self.ok &= correcto
        self.obtenido.append(("✅ " if correcto else "❌ ") + texto)


def recortar(valor, limite=900):
    texto = json.dumps(valor, ensure_ascii=False, indent=2, default=str)
    return texto if len(texto) <= limite else texto[:limite] + "\n  ... (respuesta recortada)"


def ejecutar():
    hoy = date.today()
    futuro = date.fromordinal(hoy.toordinal() + 20).isoformat()
    for u in ["coordinacion", "organizador1", "organizador2", "estudiante1", "estudiante3", "estudiante4", "estudiante5"]:
        login(u)

    def evento_valido(**cambios):
        datos = {
            "titulo": "Taller de pruebas de software",
            "descripcion": "Evento creado durante las pruebas funcionales.",
            "tipo": "TALLER",
            "lugar": "Sala de cómputo 3",
            "fecha": futuro,
            "hora_inicio": "08:00",
            "hora_fin": "10:00",
            "cupo": 25,
            "fecha_limite_inscripcion": futuro,
        }
        datos.update(cambios)
        return datos

    # ---------------- PF-01 ----------------
    p = Prueba("PF-01", "Registro y publicación de actividad válida", "RF-03, RF-04 / CA-01",
               "Organizador1 con sesión iniciada.", "201 al crear (estado BORRADOR), 200 al publicar y el evento aparece en el catálogo.")
    creado = p.paso("Crear evento válido", "POST", "/api/eventos", 201, evento_valido(), "organizador1",
                    lambda r: (r["estado"] == "BORRADOR", f"estado={r['estado']}"))
    nuevo_id = creado["id"]
    p.paso("Publicar el evento", "PATCH", f"/api/eventos/{nuevo_id}/publicar", 200, usuario="organizador1",
           verificar=lambda r: (r["estado"] == "PUBLICADO", f"estado={r['estado']}"))
    p.paso("Consultar catálogo público", "GET", "/api/eventos", 200,
           verificar=lambda r: (any(e["id"] == nuevo_id for e in r), f"evento {nuevo_id} visible en catálogo"))
    resultados.append(p)

    # ---------------- PF-02 ----------------
    p = Prueba("PF-02", "Creación de actividad con datos inválidos", "RF-03, RNF-02 / CA-01",
               "Organizador1 con sesión iniciada.", "422 en cada caso y ningún evento nuevo guardado.")
    antes = len(solicitud("GET", "/api/gestion/eventos", usuario="organizador1")[1])
    p.paso("Hora de fin anterior a la de inicio", "POST", "/api/eventos", 422,
           evento_valido(hora_inicio="10:00", hora_fin="08:00"), "organizador1")
    p.paso("Cupo en cero y título vacío", "POST", "/api/eventos", 422, evento_valido(cupo=0, titulo=""), "organizador1")
    p.paso("Fecha límite posterior al evento", "POST", "/api/eventos", 422,
           evento_valido(fecha_limite_inscripcion="2099-01-01"), "organizador1")
    p.paso("Evento con fecha pasada", "POST", "/api/eventos", 400, evento_valido(fecha="2020-01-01", fecha_limite_inscripcion="2020-01-01"), "organizador1")
    despues = len(solicitud("GET", "/api/gestion/eventos", usuario="organizador1")[1])
    p.nota(f"Eventos del organizador antes: {antes}, después: {despues} (no se guardó nada inválido)", antes == despues)
    resultados.append(p)

    # ---------------- PF-03 ----------------
    p = Prueba("PF-03", "Consulta de catálogo y detalle de evento", "RF-05 / CA-02",
               "Datos de ejemplo cargados. Sin sesión (consulta pública).", "200 con datos reales y cupos coherentes.")
    p.paso("Catálogo filtrado por tipo TALLER", "GET", "/api/eventos?tipo=TALLER", 200,
           verificar=lambda r: (all(e["tipo"] == "TALLER" for e in r), f"{len(r)} talleres"))
    p.paso("Detalle del evento 2 (Taller de Git)", "GET", "/api/eventos/2", 200,
           verificar=lambda r: (r["cupo"] == r["inscritos"] + r["cupos_disponibles"], f"cupo={r['cupo']} inscritos={r['inscritos']} disponibles={r['cupos_disponibles']}"))
    resultados.append(p)

    # ---------------- PF-04 ----------------
    p = Prueba("PF-04", "Consulta de evento inexistente", "RF-05, RNF-03",
               "Sin sesión.", "404 con mensaje controlado (sin detalles internos).")
    p.paso("Evento 99999", "GET", "/api/eventos/99999", 404)
    p.paso("Evento en borrador (no público)", "GET", "/api/eventos/6", 404)
    resultados.append(p)

    # ---------------- PF-05 ----------------
    p = Prueba("PF-05", "Inscripción válida de un participante", "RF-06, RF-07 / CA-03",
               "Estudiante3 con sesión. Taller de Git (id 2) con cupo 3 y 2 inscritos.", "201 y la inscripción aparece en «mis inscripciones».")
    insc = p.paso("Inscribirse en el evento 2", "POST", "/api/eventos/2/inscripciones", 201, usuario="estudiante3")
    p.paso("Consultar mis inscripciones", "GET", "/api/inscripciones/mias", 200, usuario="estudiante3",
           verificar=lambda r: (any(i["id"] == insc["id"] and i["estado"] == "ACTIVA" for i in r), "inscripción ACTIVA encontrada"))
    resultados.append(p)

    # ---------------- PF-06 ----------------
    p = Prueba("PF-06", "Inscripción con datos inválidos", "RF-01, RF-06, RNF-02",
               "Estudiante1 con sesión.", "422/404 controlados; nada se guarda.")
    p.paso("Identificador de evento no numérico", "POST", "/api/eventos/abc/inscripciones", 422, usuario="estudiante1")
    p.paso("Evento en borrador", "POST", "/api/eventos/6/inscripciones", 404, usuario="estudiante1")
    p.paso("Registro de cuenta con correo externo", "POST", "/api/auth/registro", 422,
           {"documento": "9999999", "nombre": "Persona Externa", "correo": "externo@gmail.com", "clave": "Clave123*"})
    p.paso("Registro con documento con letras y clave corta", "POST", "/api/auth/registro", 422,
           {"documento": "ABC", "nombre": "X", "correo": f"nuevo@{DOMINIO}", "clave": "123"})
    resultados.append(p)

    # ---------------- PF-07 ----------------
    p = Prueba("PF-07", "Intento de inscripción con cupo agotado", "RF-08 / CA-04",
               "Evento 2 con 3/3 inscritos tras PF-05. Estudiante4 con sesión.", "409 «cupo agotado» y el número de inscritos no cambia.")
    p.paso("Estudiante4 intenta inscribirse", "POST", "/api/eventos/2/inscripciones", 409, usuario="estudiante4")
    p.paso("Verificar que el cupo se conservó", "GET", "/api/eventos/2", 200,
           verificar=lambda r: (r["inscritos"] == 3 and r["cupos_disponibles"] == 0, f"inscritos={r['inscritos']} disponibles={r['cupos_disponibles']}"))
    resultados.append(p)

    # ---------------- PF-08 ----------------
    p = Prueba("PF-08", "Intento de inscripción duplicada", "RF-09 / CA-04",
               "Estudiante1 ya inscrito en el evento 1.", "409 «ya está inscrito».")
    p.paso("Estudiante1 se inscribe otra vez en el evento 1", "POST", "/api/eventos/1/inscripciones", 409, usuario="estudiante1")
    p.paso("Verificar que no hay registros repetidos", "GET", "/api/inscripciones/mias", 200, usuario="estudiante1",
           verificar=lambda r: (sum(1 for i in r if i["evento"]["id"] == 1) == 1, "una sola inscripción al evento 1"))
    resultados.append(p)

    # ---------------- PF-09 ----------------
    p = Prueba("PF-09", "Gestión de evento o asistencia sin autorización", "RF-02, RNF-01",
               "Varias sesiones con roles distintos.", "401 sin sesión y 403 con rol o dueño incorrecto.")
    p.paso("Crear evento sin iniciar sesión", "POST", "/api/eventos", 401, evento_valido())
    p.paso("Participante intenta crear evento", "POST", "/api/eventos", 403, evento_valido(), "estudiante1")
    p.paso("Organizador2 intenta cancelar evento de Organizador1", "PATCH", "/api/eventos/1/cancelar", 403, usuario="organizador2")
    p.paso("Participante intenta registrar asistencia", "PUT", "/api/eventos/1/asistencia/1", 403, {"estado": "ASISTIO"}, "estudiante1")
    p.paso("Organizador intenta ver reportes de coordinación", "GET", "/api/reportes/eventos", 403, usuario="organizador1")
    resultados.append(p)

    # ---------------- PF-10 ----------------
    p = Prueba("PF-10", "Registro y consulta de asistencia", "RF-11, RF-12 / CA-05",
               "Evento 1 se realiza hoy, con 4 inscritos. Organizador1 con sesión.", "201 al registrar, la lista muestra la asistencia asociada a evento y participante.")
    lista = p.paso("Consultar lista de participantes del evento 1", "GET", "/api/eventos/1/participantes", 200, usuario="organizador1")
    primera = lista["participantes"][0]["inscripcion_id"]
    p.paso("Registrar ASISTIO", "PUT", f"/api/eventos/1/asistencia/{primera}", 201, {"estado": "ASISTIO"}, "organizador1")
    p.paso("Consultar lista actualizada", "GET", "/api/eventos/1/participantes", 200, usuario="organizador1",
           verificar=lambda r: (any(x["inscripcion_id"] == primera and x["asistencia"] == "ASISTIO" for x in r["participantes"]), "asistencia ASISTIO guardada"))
    resultados.append(p)

    # ---------------- PF-11 ----------------
    p = Prueba("PF-11", "Información consolidada y consistencia de datos", "RF-13, RF-14 / CA-06",
               "Coordinación con sesión.", "Para cada actividad: inscritos + disponibles = cupo y asistieron + no asistieron + sin registro = inscritos; coincide con el catálogo.")
    reporte = p.paso("Reporte por actividad", "GET", "/api/reportes/eventos", 200, usuario="coordinacion")
    for fila in reporte:
        cuadra = fila["inscritos"] + fila["cupos_disponibles"] == fila["cupo"] and \
            fila["asistieron"] + fila["no_asistieron"] + fila["sin_registro"] == fila["inscritos"]
        if not cuadra:
            p.nota(f"Totales incoherentes en {fila['titulo']}", False)
    p.nota(f"{len(reporte)} actividades revisadas: totales coherentes")
    detalle = solicitud("GET", "/api/eventos/2")[1]
    fila2 = next(f for f in reporte if f["evento_id"] == 2)
    p.nota(f"Evento 2: catálogo={detalle['inscritos']} inscritos, reporte={fila2['inscritos']} inscritos", detalle["inscritos"] == fila2["inscritos"])
    p.paso("Reporte por periodo (mes)", "GET", "/api/reportes/periodos", 200, usuario="coordinacion",
           verificar=lambda r: (len(r) >= 1 and all(0 <= x["porcentaje_asistencia"] <= 100 for x in r), f"{len(r)} periodos"))
    resultados.append(p)

    # ---------------- PF-12 ----------------
    p = Prueba("PF-12", "Integración: flujo completo creación → inscripción → asistencia", "CA-01 a CA-06",
               "Servidor y base de datos en ejecución.", "Cada paso queda persistido y se refleja en los siguientes.")
    nuevo = p.paso("Organizador1 crea evento para hoy", "POST", "/api/eventos", 201,
                   evento_valido(titulo="Charla de integración", fecha=hoy.isoformat(), fecha_limite_inscripcion=hoy.isoformat(),
                                 hora_inicio="23:00", hora_fin="23:59", cupo=5), "organizador1")
    eid = nuevo["id"]
    evento_integracion["id"] = eid
    p.paso("Publicar", "PATCH", f"/api/eventos/{eid}/publicar", 200, usuario="organizador1")
    insc = p.paso("Estudiante5 se inscribe", "POST", f"/api/eventos/{eid}/inscripciones", 201, usuario="estudiante5")
    p.paso("Catálogo refleja 1 inscrito y 4 disponibles", "GET", f"/api/eventos/{eid}", 200,
           verificar=lambda r: (r["inscritos"] == 1 and r["cupos_disponibles"] == 4, f"inscritos={r['inscritos']}"))
    p.paso("Organizador1 registra asistencia", "PUT", f"/api/eventos/{eid}/asistencia/{insc['id']}", 201, {"estado": "ASISTIO"}, "organizador1")
    p.paso("Coordinación ve 100 % de asistencia en el reporte", "GET", "/api/reportes/eventos", 200, usuario="coordinacion",
           verificar=lambda r: (any(f["evento_id"] == eid and f["porcentaje_asistencia"] == 100.0 for f in r), "100 % en el reporte"))
    p.paso("El participante ve su asistencia", "GET", "/api/inscripciones/mias", 200, usuario="estudiante5",
           verificar=lambda r: (any(i["evento"]["id"] == eid and i["asistencia"] == "ASISTIO" for i in r), "asistencia visible para el participante"))
    resultados.append(p)

    # ================= Pruebas adicionales de reglas aprobadas =================
    p = Prueba("PF-13", "Cruce de horario entre actividades", "RF-10 / CA-04",
               "Estudiante1 inscrito en Taller de Git (id 2, 14:00-17:00). Seminario de BD (id 3) mismo día 15:00-16:00.", "409 por cruce de horario.")
    p.paso("Inscribirse en el evento 3", "POST", "/api/eventos/3/inscripciones", 409, usuario="estudiante1")
    resultados.append(p)

    p = Prueba("PF-14", "Inscripción después de la fecha límite", "RF-08 / CA-04",
               "Capacitación en primeros auxilios (id 4) con fecha límite ayer.", "409 fecha límite vencida.")
    p.paso("Estudiante1 intenta inscribirse", "POST", "/api/eventos/4/inscripciones", 409, usuario="estudiante1")
    resultados.append(p)

    p = Prueba("PF-15", "Cancelar inscripción libera el cupo", "RF-07 / CA-04",
               "Evento 2 lleno (3/3). Estudiante3 inscrito.", "200 al cancelar, el cupo vuelve a 1 y Estudiante4 puede inscribirse.")
    p.paso("Estudiante3 cancela su inscripción", "PATCH", f"/api/inscripciones/{insc_id_est3_ev2()}/cancelar", 200, usuario="estudiante3")
    p.paso("Cupo disponible otra vez", "GET", "/api/eventos/2", 200, verificar=lambda r: (r["cupos_disponibles"] == 1, f"disponibles={r['cupos_disponibles']}"))
    p.paso("Estudiante4 ahora sí se inscribe", "POST", "/api/eventos/2/inscripciones", 201, usuario="estudiante4")
    p.paso("Estudiante4 intenta cancelar inscripción ajena", "PATCH", "/api/inscripciones/1/cancelar", 403, usuario="estudiante4")
    resultados.append(p)

    p = Prueba("PF-16", "Asistencia fuera de las reglas", "RF-11 / CA-05",
               "Organizador1 con sesión.", "404 para quien no está inscrito en el evento; 409 si el evento no es hoy.")
    p.paso("Registrar asistencia con inscripción de otro evento", "PUT", "/api/eventos/1/asistencia/5", 404, {"estado": "ASISTIO"}, "organizador1")
    p.paso("Registrar asistencia antes del día del evento (evento 2)", "PUT", "/api/eventos/2/asistencia/5", 409, {"estado": "ASISTIO"}, "organizador1")
    p.paso("Estado de asistencia inválido", "PUT", "/api/eventos/1/asistencia/1", 422, {"estado": "TARDE"}, "organizador1")
    resultados.append(p)

    p = Prueba("PF-17", "Corrección de asistencia", "RF-12 / CA-05",
               "Asistencia registrada en PF-10.", "200 y el estado cambia a NO_ASISTIO.")
    p.paso("Corregir a NO_ASISTIO", "PUT", f"/api/eventos/1/asistencia/{primera}", 200, {"estado": "NO_ASISTIO"}, "organizador1",
           verificar=lambda r: (r["asistencia"] == "NO_ASISTIO", f"asistencia={r['asistencia']}"))
    resultados.append(p)

    p = Prueba("PF-18", "No se puede reducir el cupo por debajo de los inscritos", "RF-03 / CA-04",
               "Evento 2 con 3 inscritos.", "409.")
    e2 = solicitud("GET", "/api/eventos/2")[1]
    datos_e2 = {k: e2[k] for k in ["titulo", "descripcion", "tipo", "lugar", "fecha", "hora_inicio", "hora_fin", "fecha_limite_inscripcion"]}
    p.paso("Cambiar cupo a 1", "PUT", "/api/eventos/2", 409, {**datos_e2, "cupo": 1}, "organizador1")
    resultados.append(p)

    p = Prueba("PF-19", "Coordinación modifica y cancela eventos de cualquier organizador", "RF-15",
               "Coordinación con sesión. Evento 5 de Organizador2.", "200 al modificar y cancelar; el evento cancelado no admite inscripciones.")
    e5 = solicitud("GET", "/api/eventos/5")[1]
    datos_e5 = {k: e5[k] for k in ["titulo", "descripcion", "tipo", "lugar", "fecha", "hora_inicio", "hora_fin", "fecha_limite_inscripcion", "cupo"]}
    p.paso("Coordinación cambia el lugar", "PUT", "/api/eventos/5", 200, {**datos_e5, "lugar": "Auditorio norte"}, "coordinacion",
           verificar=lambda r: (r["lugar"] == "Auditorio norte", "lugar actualizado"))
    p.paso("Coordinación cancela el evento", "PATCH", "/api/eventos/5/cancelar", 200, usuario="coordinacion")
    p.paso("Participante intenta inscribirse al cancelado", "POST", "/api/eventos/5/inscripciones", 409, usuario="estudiante1")
    resultados.append(p)

    p = Prueba("PF-20", "Inicio de sesión", "RF-01, RF-02, RNF-01",
               "Cuentas de ejemplo.", "200 con credenciales correctas; 401 con contraseña incorrecta (mensaje genérico).")
    p.paso("Contraseña incorrecta", "POST", "/api/auth/login", 401, {"correo": f"estudiante1@{DOMINIO}", "clave": "otra"})
    p.paso("Credenciales correctas", "POST", "/api/auth/login", 200, {"correo": f"estudiante1@{DOMINIO}", "clave": CLAVE},
           verificar=lambda r: (r["usuario"]["rol"] == "PARTICIPANTE", "rol PARTICIPANTE"))
    resultados.append(p)


# Id del evento creado en PF-12 (se consulta directamente en la base de datos al final).
evento_integracion = {}
BD = Path(__file__).resolve().parents[1] / "backend" / "eventos.db"


def consulta_bd():
    """Evidencia de persistencia: lee las tablas con SQL, sin pasar por la API."""
    eid = evento_integracion.get("id")
    if eid is None or not BD.exists():
        return ["_No se encontró la base de datos local; se omite la consulta directa._"]
    con = sqlite3.connect(f"file:{BD.as_posix()}?mode=ro", uri=True)
    consultas = [
        ("Evento creado en PF-12",
         "SELECT id, titulo, estado, fecha, cupo FROM eventos WHERE id = ?"),
        ("Inscripciones del evento",
         "SELECT i.id, u.nombre, u.correo, i.estado FROM inscripciones i "
         "JOIN usuarios u ON u.id = i.participante_id WHERE i.evento_id = ?"),
        ("Asistencia registrada",
         "SELECT a.id, a.inscripcion_id, u.nombre, a.estado FROM asistencias a "
         "JOIN inscripciones i ON i.id = a.inscripcion_id JOIN usuarios u ON u.id = i.participante_id "
         "WHERE i.evento_id = ?"),
    ]
    lineas = []
    for titulo, sql in consultas:
        cursor = con.execute(sql, (eid,))
        columnas = [c[0] for c in cursor.description]
        filas = cursor.fetchall()
        lineas += ["", f"**{titulo}**", "", "```sql", sql.replace(" ?", f" {eid}"), "```", "",
                   "| " + " | ".join(columnas) + " |", "|" + "---|" * len(columnas)]
        lineas += ["| " + " | ".join(str(v) for v in fila) + " |" for fila in filas]
    con.close()
    return lineas


def insc_id_est3_ev2():
    mias = solicitud("GET", "/api/inscripciones/mias", usuario="estudiante3")[1]
    return next(i["id"] for i in mias if i["evento"]["id"] == 2 and i["estado"] == "ACTIVA")


def escribir_informe():
    aprobadas = sum(1 for p in resultados if p.ok)
    lineas = [
        "# Resultados de pruebas funcionales de la API",
        "",
        f"- **Fecha de ejecución:** {datetime.now():%Y-%m-%d %H:%M}",
        f"- **Servidor:** {BASE}",
        "- **Herramienta:** `python pruebas/ejecutar_pruebas.py` (solicitudes HTTP reales con la librería estándar)",
        "- **Datos iniciales:** base reiniciada con `python -m app.seed`",
        f"- **Resultado:** {aprobadas} de {len(resultados)} pruebas aprobadas",
        "",
        "| ID | Prueba | Requisito | Estado |",
        "|---|---|---|---|",
    ]
    for p in resultados:
        lineas.append(f"| [{p.ident}](#{p.ident.lower()}) | {p.nombre} | {p.requisito} | {'✅ Aprobada' if p.ok else '❌ Fallida'} |")
    for p in resultados:
        lineas += [
            "",
            "---",
            "",
            f"## {p.ident}",
            "",
            f"**{p.nombre}** · Requisito: {p.requisito} · Estado: {'✅ Aprobada' if p.ok else '❌ Fallida'}",
            "",
            f"- **Condiciones iniciales:** {p.condiciones}",
            f"- **Resultado esperado:** {p.esperado}",
            "",
            "| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |",
            "|---|---|---|---|---|---|---|",
        ]
        for n, s in enumerate(p.pasos, 1):
            lineas.append(
                f"| {n} | {s['descripcion']} | {s['usuario']} | `{s['metodo']} {s['ruta']}` | {s['esperado']} | {s['codigo']} | "
                f"{'✅' if s['correcto'] else '❌'} {s['detalle']} |"
            )
        if p.obtenido:
            lineas += ["", "**Verificaciones adicionales:**", ""] + [f"- {o}" for o in p.obtenido]
        lineas += ["", "<details><summary>Ver solicitudes y respuestas</summary>", ""]
        for n, s in enumerate(p.pasos, 1):
            lineas.append(f"**Paso {n}: `{s['metodo']} {s['ruta']}` → {s['codigo']}**")
            if s["datos"] is not None:
                lineas += ["", "Datos enviados:", "", "```json", recortar(s["datos"]), "```"]
            lineas += ["", "Respuesta:", "", "```json", recortar(s["respuesta"]), "```", ""]
        lineas.append("</details>")
    lineas += [
        "",
        "---",
        "",
        "## Verificación directa en la base de datos",
        "",
        "Después del flujo de integración (PF-12) se consultan las tablas de SQLite con SQL, sin usar la API, "
        "para comprobar que el evento, la inscripción y la asistencia quedaron guardados y relacionados.",
    ] + consulta_bd()
    SALIDA.parent.mkdir(exist_ok=True)
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return aprobadas


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consola de Windows
    ejecutar()
    aprobadas = escribir_informe()
    for p in resultados:
        print(f"{p.ident}  {'APROBADA' if p.ok else 'FALLIDA '}  {p.nombre}")
    print(f"\n{aprobadas}/{len(resultados)} pruebas aprobadas. Evidencia: {SALIDA}")
    sys.exit(0 if aprobadas == len(resultados) else 1)
