# Plan y resultados de pruebas funcionales

Las pruebas verifican la API REST, las reglas de inscripción, cupos y asistencia, y la integración interfaz → API → base de datos. Son **pruebas funcionales documentadas**: cada una se puede repetir con los pasos indicados.

## 1. Cómo reproducir las pruebas

**Opción A — Script reproducible (pruebas de API PF-01 a PF-20)**

```bash
cd backend
python -m app.seed                     # 1. Reinicia la base con datos ficticios
python -m uvicorn app.main:app         # 2. Inicia el servidor (dejar abierta esta terminal)
```

```bash
python pruebas/ejecutar_pruebas.py     # 3. En otra terminal, desde la raíz del proyecto
```

El script envía solicitudes HTTP reales, compara los códigos obtenidos con los esperados y guarda cada solicitud y respuesta en [`evidencias/resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md).

**Opción B — Documentación interactiva de la API**

1. Abrir `http://127.0.0.1:8000/docs`.
2. Ejecutar `POST /api/auth/login` con una cuenta de prueba y copiar el `token`.
3. Pulsar **Authorize** y pegar el token.
4. Ejecutar el endpoint de la prueba con los datos indicados.

**Opción C — Interfaz web (pruebas de integración PF-12 e IU-01 a IU-06)**: abrir `http://127.0.0.1:8000` y seguir los pasos de la sección 3.

### Datos de prueba (ficticios)

Contraseña de todas las cuentas: `Clave123*`

| Correo | Rol | Nombre |
|---|---|---|
| coordinacion@institucion.edu.co | Coordinación | Laura Gómez |
| organizador1@institucion.edu.co | Organizador | Carlos Ruiz |
| organizador2@institucion.edu.co | Organizador | Marta Díaz |
| estudiante1@institucion.edu.co … estudiante5@ | Participante | Ana, Bruno, Camila, Daniel, Elena |
| docente1@institucion.edu.co | Participante | Felipe Moreno |

| Id | Evento de ejemplo | Para qué sirve |
|---|---|---|
| 1 | Conferencia IA en la educación (**hoy**) | Registrar asistencia |
| 2 | Taller de Git y GitHub (en 3 días, **cupo 3**, 2 inscritos) | Llenar el cupo y probar cupo agotado |
| 3 | Seminario de bases de datos (mismo día y hora que el 2) | Probar cruce de horario |
| 4 | Capacitación primeros auxilios (fecha límite **ayer**) | Probar fecha límite vencida |
| 5 | Conferencia de emprendimiento (Organizador 2) | Probar permisos entre organizadores |
| 6 | Seminario de investigación (**borrador**) | Probar publicación |
| 7, 8, 10 | Eventos pasados con asistencia | Reportes por actividad y por mes |
| 9 | Taller de fotografía (**cancelado**) | Estado cancelado |

---

## 2. Pruebas de API y reglas de negocio

| ID | Prueba | Requisito | Condiciones iniciales | Pasos y datos de entrada | Método y ruta | Resultado esperado | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|---|---|---|---|
| PF-01 | Registro y publicación de actividad válida | RF-03, RF-04 / CA-01 | Sesión de organizador1 | Crear evento válido; publicarlo; consultar catálogo | `POST /api/eventos` → `PATCH /api/eventos/{id}/publicar` → `GET /api/eventos` | 201 (Borrador) → 200 (Publicado) → el evento aparece en el catálogo | Igual al esperado: 201 (Borrador) → 200 (Publicado) → el evento aparece en el catálogo | ✅ | [PF-01](../evidencias/resultados_pruebas_api.md#pf-01) |
| PF-02 | Creación con datos inválidos | RF-03, RNF-02 | Sesión de organizador1 | Hora fin < inicio; cupo 0 y título vacío; límite posterior al evento; fecha pasada | `POST /api/eventos` | 422 / 400 y el número de eventos no cambia | Igual al esperado: 422 / 400 y el número de eventos no cambia | ✅ | [PF-02](../evidencias/resultados_pruebas_api.md#pf-02) |
| PF-03 | Consulta de catálogo y detalle | RF-05 / CA-02 | Sin sesión | Filtrar por TALLER; ver detalle del evento 2 | `GET /api/eventos?tipo=TALLER`, `GET /api/eventos/2` | 200; cupo = inscritos + disponibles | Igual al esperado: 200; cupo = inscritos + disponibles | ✅ | [PF-03](../evidencias/resultados_pruebas_api.md#pf-03) |
| PF-04 | Evento inexistente | RF-05, RNF-03 | Sin sesión | Consultar id 99999 y un borrador | `GET /api/eventos/99999`, `GET /api/eventos/6` | 404 con mensaje controlado | Igual al esperado: 404 con mensaje controlado | ✅ | [PF-04](../evidencias/resultados_pruebas_api.md#pf-04) |
| PF-05 | Inscripción válida | RF-06 / CA-03 | Estudiante3; evento 2 con 2/3 | Inscribirse y consultar «mis inscripciones» | `POST /api/eventos/2/inscripciones`, `GET /api/inscripciones/mias` | 201; inscripción ACTIVA recuperable | Igual al esperado: 201; inscripción ACTIVA recuperable | ✅ | [PF-05](../evidencias/resultados_pruebas_api.md#pf-05) |
| PF-06 | Inscripción con datos inválidos | RF-01, RF-06, RNF-02 | Estudiante1 | Id no numérico; evento borrador; registro con correo externo; documento con letras y clave corta | `POST /api/eventos/abc/inscripciones`, `POST /api/auth/registro` | 422 / 404, nada se guarda | Igual al esperado: 422 / 404, nada se guarda | ✅ | [PF-06](../evidencias/resultados_pruebas_api.md#pf-06) |
| PF-07 | Cupo agotado | RF-08 / CA-04 | Evento 2 lleno (3/3) | Estudiante4 intenta inscribirse | `POST /api/eventos/2/inscripciones` | 409 «cupo agotado»; inscritos sigue en 3 | Igual al esperado: 409 «cupo agotado»; inscritos sigue en 3 | ✅ | [PF-07](../evidencias/resultados_pruebas_api.md#pf-07) |
| PF-08 | Inscripción duplicada | RF-09 / CA-04 | Estudiante1 inscrito en evento 1 | Inscribirse otra vez | `POST /api/eventos/1/inscripciones` | 409 «ya está inscrito»; una sola inscripción | Igual al esperado: 409 «ya está inscrito»; una sola inscripción | ✅ | [PF-08](../evidencias/resultados_pruebas_api.md#pf-08) |
| PF-09 | Acciones sin autorización | RF-02, RNF-01 | Varias sesiones | Crear evento sin sesión / como participante; organizador2 cancela evento ajeno; participante registra asistencia; organizador ve reportes | Varias | 401 sin sesión; 403 sin permiso | Igual al esperado: 401 sin sesión; 403 sin permiso | ✅ | [PF-09](../evidencias/resultados_pruebas_api.md#pf-09) |
| PF-10 | Registro y consulta de asistencia | RF-11, RF-12 / CA-05 | Evento 1 es hoy | Ver lista; marcar ASISTIO; ver lista | `GET /api/eventos/1/participantes`, `PUT /api/eventos/1/asistencia/{id}` | 201; la lista muestra ASISTIO para ese participante | Igual al esperado: 201; la lista muestra ASISTIO para ese participante | ✅ | [PF-10](../evidencias/resultados_pruebas_api.md#pf-10) |
| PF-11 | Consolidado y consistencia | RF-13, RF-14 / CA-06 | Sesión de coordinación | Reporte por actividad y por periodo; comparar con catálogo | `GET /api/reportes/eventos`, `GET /api/reportes/periodos` | Totales cuadran en todas las actividades y coinciden con el catálogo | Igual al esperado: Totales cuadran en todas las actividades y coinciden con el catálogo | ✅ | [PF-11](../evidencias/resultados_pruebas_api.md#pf-11) |
| PF-12 | Integración completa | CA-01 a CA-06 | Servidor en ejecución | Crear evento hoy → publicar → inscribir → ver cupo → registrar asistencia → reporte 100 % → participante ve su asistencia | Varias | Cada paso queda guardado y se refleja en el siguiente | Igual al esperado: Cada paso queda guardado y se refleja en el siguiente | ✅ | [PF-12](../evidencias/resultados_pruebas_api.md#pf-12) |
| PF-13 | Cruce de horario | RF-10 / CA-04 | Estudiante1 en evento 2 (14-17 h) | Inscribirse en evento 3 (15-16 h, mismo día) | `POST /api/eventos/3/inscripciones` | 409 cruce de horario | Igual al esperado: 409 cruce de horario | ✅ | [PF-13](../evidencias/resultados_pruebas_api.md#pf-13) |
| PF-14 | Fecha límite vencida | RF-08 / CA-04 | Evento 4 con límite ayer | Inscribirse | `POST /api/eventos/4/inscripciones` | 409 | Igual al esperado: 409 | ✅ | [PF-14](../evidencias/resultados_pruebas_api.md#pf-14) |
| PF-15 | Cancelar libera cupo | RF-07 / CA-04 | Evento 2 lleno | Estudiante3 cancela; estudiante4 se inscribe; estudiante4 intenta cancelar inscripción ajena | `PATCH /api/inscripciones/{id}/cancelar`, `POST ...` | 200 → disponibles 1 → 201 → 403 | Igual al esperado: 200 → disponibles 1 → 201 → 403 | ✅ | [PF-15](../evidencias/resultados_pruebas_api.md#pf-15) |
| PF-16 | Asistencia fuera de reglas | RF-11 / CA-05 | Organizador1 | Inscripción de otro evento; evento que no es hoy; estado inválido | `PUT /api/eventos/{id}/asistencia/{id}` | 404 / 409 / 422 | Igual al esperado: 404 / 409 / 422 | ✅ | [PF-16](../evidencias/resultados_pruebas_api.md#pf-16) |
| PF-17 | Corrección de asistencia | RF-12 / CA-05 | Asistencia de PF-10 | Cambiar a NO_ASISTIO | `PUT /api/eventos/1/asistencia/{id}` | 200 y estado corregido | Igual al esperado: 200 y estado corregido | ✅ | [PF-17](../evidencias/resultados_pruebas_api.md#pf-17) |
| PF-18 | Reducir cupo bajo inscritos | RF-03 / CA-04 | Evento 2 con 3 inscritos | Cambiar cupo a 1 | `PUT /api/eventos/2` | 409 | Igual al esperado: 409 | ✅ | [PF-18](../evidencias/resultados_pruebas_api.md#pf-18) |
| PF-19 | Coordinación modifica y cancela | RF-15 | Evento 5 de organizador2 | Coordinación cambia lugar y cancela; participante intenta inscribirse | `PUT`, `PATCH .../cancelar`, `POST .../inscripciones` | 200, 200, 409 | Igual al esperado: 200, 200, 409 | ✅ | [PF-19](../evidencias/resultados_pruebas_api.md#pf-19) |
| PF-20 | Inicio de sesión | RF-02, RNF-01 | Cuentas de prueba | Clave incorrecta; clave correcta | `POST /api/auth/login` | 401 genérico; 200 con rol | Igual al esperado: 401 genérico; 200 con rol | ✅ | [PF-20](../evidencias/resultados_pruebas_api.md#pf-20) |

**Resultado obtenido:** 20 de 20 pruebas aprobadas. El detalle de cada paso (datos enviados, código esperado, código obtenido y respuesta) está en [`evidencias/resultados_pruebas_api.md`](../evidencias/resultados_pruebas_api.md), que al final incluye una **consulta SQL directa a la base de datos** para comprobar que el evento, la inscripción y la asistencia del flujo PF-12 quedaron guardados y relacionados.

---

## 3. Pruebas de integración desde la interfaz

Condición inicial común: base reiniciada con `python -m app.seed` y servidor en ejecución. Se ejecutan en el navegador sobre `http://127.0.0.1:8000`.

| ID | Prueba | Requisito | Condiciones iniciales | Pasos | Resultado esperado | Resultado obtenido | Estado | Evidencia |
|---|---|---|---|---|---|---|---|---|
| IU-01 | Menú según rol | RF-02, RNF-05 | Cuentas de prueba | Ingresar como participante, organizador y coordinación | Cada rol ve solo sus opciones | Participante: Catálogo y Mis inscripciones; organizador: Catálogo y Gestión; coordinación: además Reportes | ✅ | `capturas/02_inscripcion_exitosa.jpg`, `03_gestion.jpg`, `07_reportes.jpg` |
| IU-02 | Crear y publicar desde la interfaz | CA-01 | Sesión de organizador1 | Gestión → Crear evento → Guardar → Publicar → Catálogo | El evento queda en Borrador, no se ve en el catálogo; al publicarlo aparece con sus cupos | Igual al esperado | ✅ | `capturas/04_crear_evento.jpg`, `03_gestion.jpg` |
| IU-03 | Inscripción y cupo en pantalla | CA-02, CA-03 | Taller de Git con 2/3 inscritos | Estudiante3 → Catálogo → Taller de Git → Inscribirme | Mensaje verde; la barra queda roja con 0 de 3 y la tarjeta muestra «Cupo agotado» a todas las personas (también a quienes ya están inscritos, junto con «Estás inscrito») | Igual al esperado | ✅ | `capturas/02_inscripcion_exitosa.jpg`, `01_catalogo.jpg` |
| IU-04 | Rechazo visible | CA-04 | Estudiante1 inscrito en Taller de Git | Estudiante1 → Inscribirme en Seminario de BD (mismo horario) | Mensaje rojo «Ya está inscrito en … horario que se cruza»; los cupos no cambian | Igual al esperado | ✅ | `capturas/05_rechazo_cruce.jpg` |
| IU-05 | Asistencia | CA-05 | Conferencia IA es hoy, 4 inscritos | Organizador1 → Participantes y asistencia → Asistió / No asistió | Indicadores y lista se actualizan y el botón marcado queda resaltado | Igual al esperado (1 asistió, 1 no asistió, 2 sin registro, 25 %) | ✅ | `capturas/06_asistencia.jpg` |
| IU-06 | Reportes | CA-06 | Sesión de coordinación | Coordinación → Reportes | Gráfica por mes y tabla por actividad con totales coherentes | Igual al esperado | ✅ | `capturas/07_reportes.jpg` |
| IU-07 | Acceso directo sin permiso | RNF-01 | Sin sesión | Abrir `http://127.0.0.1:8000/reportes.html` | Redirige a la página de acceso | Redirige a `login.html?volver=/reportes.html` | ✅ | `capturas/08_acceso_sin_sesion.jpg` |
| IU-08 | Persistencia | RNF-04 | Evento creado en PF-12 | Detener el servidor (Ctrl+C), iniciarlo otra vez y consultar el evento | Los datos creados siguen guardados | El evento, su inscripción y su asistencia siguen disponibles tras reiniciar | ✅ | `capturas/09_persistencia_reinicio.jpg` y consulta SQL en `resultados_pruebas_api.md` |
