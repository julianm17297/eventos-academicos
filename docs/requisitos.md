# Requisitos del sistema — Eventos y actividades académicas

> Proyecto Final PF-04 · Aplicaciones y Servicios Web · Tecnología en Desarrollo de Software

Este documento define **qué** implementa la aplicación. Es la base del desarrollo y de las pruebas funcionales.

---

## 1. Método de levantamiento de información

| Aspecto | Detalle |
|---|---|
| Técnica | Entrevista estructurada con el docente en el rol de representante de la organización |
| Medio | Chat de la asignatura (preguntas enviadas por escrito y respuestas por el mismo medio) |
| Preparación | Análisis del enunciado (Actividad 1): situación actual, actores, límites del alcance y condiciones CA-01 a CA-06 |
| Enfoque de las preguntas | Se agruparon en 3 preguntas con subpreguntas cerradas para obtener respuestas concretas y convertibles en reglas de negocio |

### Problemas detectados en el enunciado (insumo para las preguntas)

| Problema de la situación actual | Lo que había que definir |
|---|---|
| Inscripciones duplicadas | Cómo identificar a una persona y qué hacer con un intento repetido |
| No se conoce el número real de inscritos ni los cupos | Cuándo se ocupa o libera un cupo |
| Divulgación dispersa | Datos y estados del evento; quién autoriza publicar |
| Asistencia difícil de consolidar | Cómo, cuándo y quién registra la asistencia; qué reportes se necesitan |
| Actores con responsabilidades generales | Permisos de cada rol |

---

## 2. Registro de la entrevista

### Pregunta 1 — Participantes, identificación y permisos

| Subpregunta | Respuesta del representante | Decisión resultante |
|---|---|---|
| ¿Quiénes pueden inscribirse? | Solo personas de la institución. | Solo se aceptan cuentas con correo institucional `@institucion.edu.co` (RN-01). |
| ¿Con qué dato se identifica a una persona? | Es una decisión de desarrollo, no del cliente. | Se usan correo institucional y documento como datos únicos. |
| ¿El organizador administra solo sus actividades o todas? | También es decisión de desarrollo. | Cada organizador gestiona solo sus propios eventos (RN-13). |
| ¿Qué puede hacer la coordinación? | Consultar, modificar y cancelar. | La coordinación consulta, modifica y cancela cualquier evento (RN-14). |

### Pregunta 2 — Ciclo de vida del evento y reglas de cupos

| Subpregunta | Respuesta | Decisión resultante |
|---|---|---|
| ¿La publicación requiere autorización? | No requiere autorización. | El organizador publica directamente su evento. |
| ¿Hay fecha límite de inscripción? | Sí hay fecha límite. | Cada evento tiene `fecha_limite_inscripcion` (RN-03). |
| ¿El participante puede cancelar su inscripción? | Sí puede cancelar. | Cancelación disponible hasta antes del inicio del evento (RN-07). |
| ¿Se puede reducir el cupo con inscritos? | Hay un límite de personas que pueden inscribirse. | El cupo es el límite máximo; no puede quedar por debajo de los inscritos (RN-12). |
| ¿Qué pasa con el cupo agotado? | Se rechaza. | Sin lista de espera: la inscripción se rechaza (RN-04). |
| ¿Se permiten actividades con horario cruzado? | No se permite estar en dos actividades en los mismos horarios. | Se rechaza la inscripción con cruce de horario (RN-06). |

### Pregunta 3 — Asistencia e información consolidada

| Subpregunta | Respuesta | Decisión resultante |
|---|---|---|
| ¿Cuándo se registra la asistencia? | El día del evento y en cada actividad. | El registro se habilita el día del evento, por actividad (RN-08). |
| ¿Qué estados de asistencia hay? | Asistió o no asistió. | Estados `ASISTIO` y `NO_ASISTIO` (RN-09). |
| ¿Se puede corregir un registro? | Sí. | El organizador o la coordinación pueden corregirlo (RN-10). |
| ¿Se registra asistencia a no inscritos? | No. | Solo inscripciones activas (RN-11). |
| ¿Qué información consolidada necesita la coordinación? | Porcentaje de asistencia por actividad y por periodos. | Reportes por actividad y por mes (RF-13, RF-14). |

Además, el representante indicó que el proyecto debe desarrollarse en un repositorio nuevo.

### Acuerdos y decisiones aprobadas

**Acuerdos:** todas las decisiones de las tablas anteriores quedaron confirmadas por el representante o asignadas por él al equipo de desarrollo.

**Decisiones complementarias:** los siguientes puntos se definieron después de la entrevista y fueron aprobados por el docente en la revisión del alcance. Forman parte de la especificación al mismo nivel que las reglas de negocio.

| ID | Decisión | Motivo |
|---|---|---|
| D-01 | Al cancelar una inscripción, el cupo queda libre otra vez. | Consecuencia lógica de "sí puede cancelar" y del límite de cupo. |
| D-02 | Quien canceló puede volver a inscribirse si hay cupo y no ha vencido la fecha límite. | Se reutiliza el mismo registro para no duplicar. |
| D-03 | La cancelación se permite hasta antes de la hora de inicio del evento. | Evita cancelar eventos ya realizados. |
| D-04 | El "periodo" de los reportes es el **mes** (AAAA-MM). | El reporte permite además filtrar por rango de fechas. |
| D-05 | Las cuentas de organizador y coordinación las crea la institución; el registro público crea solo participantes. | Evita que cualquiera se asigne un rol con más permisos. |
| D-06 | Cada evento ocurre en un solo día (fecha, hora de inicio y hora de fin). | Simplifica el control de cruces de horario. |
| D-07 | La asistencia se registra por primera vez el día del evento; las correcciones se aceptan después. | Combina "el día del evento" con "sí se puede corregir". |

---

## 3. Actores y permisos

| Actor | Rol en el sistema | Puede hacer |
|---|---|---|
| Visitante | (sin sesión) | Ver el catálogo de eventos publicados y su disponibilidad. |
| Participante | `PARTICIPANTE` | Registrarse con correo institucional, inscribirse, ver y cancelar sus inscripciones, ver su asistencia. |
| Organizador | `ORGANIZADOR` | Crear, modificar, publicar y cancelar **sus** eventos; ver la lista de inscritos; registrar y corregir asistencia. |
| Coordinación | `COORDINACION` | Consultar, modificar y cancelar **todos** los eventos; registrar/corregir asistencia; ver reportes consolidados. |

## 4. Procesos principales

1. **Publicación:** el organizador crea el evento (queda en *Borrador*) → lo publica (*Publicado*) → aparece en el catálogo.
2. **Inscripción:** el participante inicia sesión → elige un evento → el sistema verifica las reglas → guarda la inscripción o la rechaza con un mensaje claro.
3. **Cancelación:** el participante cancela → el cupo queda libre.
4. **Asistencia:** el día del evento, el organizador abre la lista de inscritos y marca *Asistió* / *No asistió*; puede corregirlo.
5. **Seguimiento:** la coordinación consulta el porcentaje de asistencia por actividad y por mes.

## 5. Reglas de negocio

| ID | Regla |
|---|---|
| RN-01 | Solo personas de la institución (correo `@institucion.edu.co`) pueden crear cuenta. |
| RN-02 | Solo se puede inscribir en eventos **publicados**. Los borradores no son visibles al público. |
| RN-03 | No se aceptan inscripciones después de la fecha límite del evento. |
| RN-04 | Si el cupo está agotado, la inscripción se rechaza (no hay lista de espera). |
| RN-05 | Una persona no puede inscribirse dos veces en el mismo evento. |
| RN-06 | Una persona no puede estar inscrita en dos actividades cuyos horarios se crucen. |
| RN-07 | El participante puede cancelar su inscripción antes del inicio; el cupo se libera. |
| RN-08 | La asistencia se registra el día del evento, por cada actividad. |
| RN-09 | Los estados de asistencia son *Asistió* y *No asistió*. |
| RN-10 | Un registro de asistencia puede corregirse. |
| RN-11 | No se registra asistencia a personas sin inscripción activa en el evento. |
| RN-12 | El cupo de un evento no puede ser menor que el número de inscritos actuales. |
| RN-13 | Un organizador solo gestiona los eventos que él creó. |
| RN-14 | La coordinación puede consultar, modificar y cancelar cualquier evento. |
| RN-15 | Un evento cancelado no admite inscripciones ni registro de asistencia. |
| RN-16 | La fecha límite de inscripción no puede ser posterior a la fecha del evento, y la hora de fin debe ser posterior a la de inicio. |

---

## 6. Requisitos funcionales

| ID | Requisito | Prioridad | Reglas | CA |
|---|---|---|---|---|
| RF-01 | Registrar cuentas de participantes con documento, nombre, correo institucional y contraseña. | Alta | RN-01 | CA-03 |
| RF-02 | Iniciar y cerrar sesión; cada usuario solo accede a las funciones de su rol. | Alta | RN-13, RN-14 | Todas |
| RF-03 | Crear y modificar eventos (título, descripción, tipo, lugar, fecha, horario, cupo, fecha límite). | Alta | RN-12, RN-16 | CA-01 |
| RF-04 | Publicar un evento en borrador para que aparezca en el catálogo. | Alta | RN-02 | CA-01 |
| RF-05 | Consultar el catálogo de eventos publicados y el detalle de cada uno con cupos disponibles. | Alta | RN-02 | CA-02 |
| RF-06 | Inscribirse en un evento publicado. | Alta | RN-02…RN-06 | CA-03 |
| RF-07 | Consultar y cancelar las propias inscripciones. | Alta | RN-07 | CA-03, CA-04 |
| RF-08 | Rechazar inscripciones con cupo agotado o fuera de la fecha límite. | Alta | RN-03, RN-04 | CA-04 |
| RF-09 | Rechazar inscripciones duplicadas. | Alta | RN-05 | CA-04 |
| RF-10 | Rechazar inscripciones con cruce de horario. | Alta | RN-06 | CA-04 |
| RF-11 | Registrar la asistencia de los inscritos el día del evento. | Alta | RN-08, RN-09, RN-11 | CA-05 |
| RF-12 | Consultar la lista de participantes con su asistencia y corregir registros. | Alta | RN-10 | CA-05 |
| RF-13 | Reporte de coordinación por actividad: cupo, inscritos, disponibles, asistieron, no asistieron y % de asistencia. | Alta | — | CA-06 |
| RF-14 | Reporte de coordinación por periodo (mes) con % de asistencia, filtrable por fechas. | Alta | — | CA-06 |
| RF-15 | Cancelar eventos (organizador dueño o coordinación). | Media | RN-13…RN-15 | CA-01 |

## 7. Requisitos no funcionales

| ID | Requisito |
|---|---|
| RNF-01 | **Seguridad:** contraseñas cifradas (PBKDF2-SHA256 con sal); acceso con token de sesión; permisos validados en el servidor (401 sin sesión, 403 sin permiso). |
| RNF-02 | **Validación:** el servidor valida todos los datos aunque la solicitud no venga de la interfaz (422 con mensajes claros). |
| RNF-03 | **Manejo de errores:** respuestas con códigos HTTP correctos y mensajes en español sin información interna. |
| RNF-04 | **Persistencia:** los datos se guardan en una base de datos relacional con llaves y restricciones de integridad. |
| RNF-05 | **Usabilidad:** interfaz web en español que muestra solo las opciones del rol y explica por qué se rechaza una acción. |
| RNF-06 | **Instalación:** la aplicación se ejecuta localmente con instrucciones reproducibles, sin Docker ni nube. |
| RNF-07 | **Privacidad:** se usan solo datos ficticios; no hay secretos en el repositorio (`.env` excluido). |

---

## 8. Historias de usuario y criterios de aceptación

**HU-01 — Publicar un evento** (RF-03, RF-04)
*Como* organizador *quiero* crear y publicar una actividad *para* que la comunidad pueda inscribirse.
- Dado un evento con datos válidos, al guardarlo queda en *Borrador* y no aparece en el catálogo.
- Al publicarlo, aparece en el catálogo con todos sus cupos disponibles.
- Si la hora de fin es anterior a la de inicio, el cupo es 0 o la fecha ya pasó, se rechaza y no se guarda nada.

**HU-02 — Consultar eventos** (RF-05)
*Como* participante *quiero* ver los eventos y sus cupos *para* elegir en cuál inscribirme.
- El catálogo muestra solo eventos publicados (o cancelados, marcados como tales).
- Los cupos disponibles = cupo − inscritos activos guardados en la base de datos.

**HU-03 — Inscribirse** (RF-06, RF-08, RF-09, RF-10)
*Como* participante *quiero* inscribirme en una actividad *para* asegurar mi cupo.
- Si cumple todas las reglas, la inscripción queda *Activa* y aparece en "Mis inscripciones".
- Se rechaza con mensaje si: el cupo está agotado, ya pasó la fecha límite, ya estaba inscrito, o tiene otra actividad con horario cruzado.
- Un rechazo no modifica el número de inscritos.

**HU-04 — Cancelar inscripción** (RF-07)
*Como* participante *quiero* cancelar mi inscripción *para* liberar el cupo si no puedo asistir.
- Solo puedo cancelar mis inscripciones y antes del inicio del evento; el cupo disponible aumenta en 1.

**HU-05 — Registrar asistencia** (RF-11, RF-12)
*Como* organizador *quiero* marcar quién asistió *para* tener la asistencia real del evento.
- El día del evento puedo marcar *Asistió* / *No asistió* a cada inscrito activo; antes de ese día se rechaza.
- Puedo corregir un registro; no puedo registrar a alguien no inscrito.

**HU-06 — Consultar información consolidada** (RF-13, RF-14)
*Como* coordinación *quiero* ver el porcentaje de asistencia por actividad y por periodo *para* supervisar los eventos.
- Para cada actividad: inscritos + disponibles = cupo, y asistieron + no asistieron + sin registro = inscritos.
- Por periodo (mes): % = asistieron ÷ inscritos de los eventos realizados.

**HU-07 — Control de acceso** (RF-01, RF-02)
*Como* institución *quiero* que cada persona haga solo lo que su rol permite *para* proteger la información.
- Solo se registran correos institucionales; sin sesión se responde 401; con un rol sin permiso, 403.
- Un organizador no puede modificar ni cancelar eventos de otro organizador.

---

## 9. Priorización y alcance aprobado

| Prioridad | Incluye |
|---|---|
| **Imprescindible** (CA-01 a CA-06) | RF-01 a RF-14 |
| **Importante** | RF-15 (cancelación de eventos) |
| **Fuera de alcance** | Pagos, videoconferencias, SMS/WhatsApp, certificados firmados, integración con sistemas institucionales, lectura de QR, lista de espera, recuperación de contraseña por correo. |

**Revisión del alcance:** esta especificación (alcance, reglas, decisiones complementarias D-01 a D-07 y criterios de aceptación) fue revisada y **aprobada por el docente**, en su rol de representante de la organización. No quedan cuestiones pendientes.
