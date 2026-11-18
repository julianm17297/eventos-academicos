# Resultados de pruebas funcionales de la API

- **Fecha de ejecución:** 2026-11-18 11:08
- **Servidor:** http://127.0.0.1:8000
- **Herramienta:** `python pruebas/ejecutar_pruebas.py` (solicitudes HTTP reales con la librería estándar)
- **Datos iniciales:** base reiniciada con `python -m app.seed`
- **Resultado:** 20 de 20 pruebas aprobadas

| ID | Prueba | Requisito | Estado |
|---|---|---|---|
| [PF-01](#pf-01) | Registro y publicación de actividad válida | RF-03, RF-04 / CA-01 | ✅ Aprobada |
| [PF-02](#pf-02) | Creación de actividad con datos inválidos | RF-03, RNF-02 / CA-01 | ✅ Aprobada |
| [PF-03](#pf-03) | Consulta de catálogo y detalle de evento | RF-05 / CA-02 | ✅ Aprobada |
| [PF-04](#pf-04) | Consulta de evento inexistente | RF-05, RNF-03 | ✅ Aprobada |
| [PF-05](#pf-05) | Inscripción válida de un participante | RF-06, RF-07 / CA-03 | ✅ Aprobada |
| [PF-06](#pf-06) | Inscripción con datos inválidos | RF-01, RF-06, RNF-02 | ✅ Aprobada |
| [PF-07](#pf-07) | Intento de inscripción con cupo agotado | RF-08 / CA-04 | ✅ Aprobada |
| [PF-08](#pf-08) | Intento de inscripción duplicada | RF-09 / CA-04 | ✅ Aprobada |
| [PF-09](#pf-09) | Gestión de evento o asistencia sin autorización | RF-02, RNF-01 | ✅ Aprobada |
| [PF-10](#pf-10) | Registro y consulta de asistencia | RF-11, RF-12 / CA-05 | ✅ Aprobada |
| [PF-11](#pf-11) | Información consolidada y consistencia de datos | RF-13, RF-14 / CA-06 | ✅ Aprobada |
| [PF-12](#pf-12) | Integración: flujo completo creación → inscripción → asistencia | CA-01 a CA-06 | ✅ Aprobada |
| [PF-13](#pf-13) | Cruce de horario entre actividades | RF-10 / CA-04 | ✅ Aprobada |
| [PF-14](#pf-14) | Inscripción después de la fecha límite | RF-08 / CA-04 | ✅ Aprobada |
| [PF-15](#pf-15) | Cancelar inscripción libera el cupo | RF-07 / CA-04 | ✅ Aprobada |
| [PF-16](#pf-16) | Asistencia fuera de las reglas | RF-11 / CA-05 | ✅ Aprobada |
| [PF-17](#pf-17) | Corrección de asistencia | RF-12 / CA-05 | ✅ Aprobada |
| [PF-18](#pf-18) | No se puede reducir el cupo por debajo de los inscritos | RF-03 / CA-04 | ✅ Aprobada |
| [PF-19](#pf-19) | Coordinación modifica y cancela eventos de cualquier organizador | RF-15 | ✅ Aprobada |
| [PF-20](#pf-20) | Inicio de sesión | RF-01, RF-02, RNF-01 | ✅ Aprobada |

---

## PF-01

**Registro y publicación de actividad válida** · Requisito: RF-03, RF-04 / CA-01 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Organizador1 con sesión iniciada.
- **Resultado esperado:** 201 al crear (estado BORRADOR), 200 al publicar y el evento aparece en el catálogo.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Crear evento válido | organizador1 | `POST /api/eventos` | 201 | 201 | ✅ estado=BORRADOR |
| 2 | Publicar el evento | organizador1 | `PATCH /api/eventos/11/publicar` | 200 | 200 | ✅ estado=PUBLICADO |
| 3 | Consultar catálogo público | (sin sesión) | `GET /api/eventos` | 200 | 200 | ✅ evento 11 visible en catálogo |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos` → 201**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08"
}
```

Respuesta:

```json
{
  "id": 11,
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00:00",
  "hora_fin": "10:00:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08",
  "estado": "BORRADOR",
  "inscritos": 0,
  "cupos_disponibles": 25,
  "inscripciones_abiertas": false,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 2: `PATCH /api/eventos/11/publicar` → 200**

Respuesta:

```json
{
  "id": 11,
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00:00",
  "hora_fin": "10:00:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08",
  "estado": "PUBLICADO",
  "inscritos": 0,
  "cupos_disponibles": 25,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 3: `GET /api/eventos` → 200**

Respuesta:

```json
[
  {
    "id": 1,
    "titulo": "Conferencia: Inteligencia artificial en la educación",
    "descripcion": "Conferencia: Inteligencia artificial en la educación. Actividad académica abierta a la comunidad institucional.",
    "tipo": "CONFERENCIA",
    "lugar": "Auditorio principal",
    "fecha": "2026-11-18",
    "hora_inicio": "07:00:00",
    "hora_fin": "09:00:00",
    "cupo": 30,
    "fecha_limite_inscripcion": "2026-11-18",
    "estado": "PUBLICADO",
    "inscritos": 4,
    "cupos_disponibles": 26,
    "inscripciones_abiertas": true,
    "organizador": {
      "id": 2,
      "nombre": "Carlos Ruiz"
    }
  },
  {
    "id": 2,
    "titulo": "Taller de Git y GitHub",
    "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
    "tipo": "TALLER",
    "lugar": "Sala de cómputo 2",
    "fecha": "2026-11-21",
    "hora_inicio": "14:00:00",
  
  ... (respuesta recortada)
```

</details>

---

## PF-02

**Creación de actividad con datos inválidos** · Requisito: RF-03, RNF-02 / CA-01 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Organizador1 con sesión iniciada.
- **Resultado esperado:** 422 en cada caso y ningún evento nuevo guardado.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Hora de fin anterior a la de inicio | organizador1 | `POST /api/eventos` | 422 | 422 | ✅  |
| 2 | Cupo en cero y título vacío | organizador1 | `POST /api/eventos` | 422 | 422 | ✅  |
| 3 | Fecha límite posterior al evento | organizador1 | `POST /api/eventos` | 422 | 422 | ✅  |
| 4 | Evento con fecha pasada | organizador1 | `POST /api/eventos` | 400 | 400 | ✅  |

**Verificaciones adicionales:**

- ✅ Eventos del organizador antes: 6, después: 6 (no se guardó nada inválido)

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos` → 422**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "10:00",
  "hora_fin": "08:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "La hora de fin debe ser posterior a la hora de inicio."
  ]
}
```

**Paso 2: `POST /api/eventos` → 422**

Datos enviados:

```json
{
  "titulo": "",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 0,
  "fecha_limite_inscripcion": "2026-12-08"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "titulo: String should have at least 3 characters",
    "cupo: Input should be greater than 0"
  ]
}
```

**Paso 3: `POST /api/eventos` → 422**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2099-01-01"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "La fecha límite de inscripción no puede ser posterior a la fecha del evento."
  ]
}
```

**Paso 4: `POST /api/eventos` → 400**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2020-01-01",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2020-01-01"
}
```

Respuesta:

```json
{
  "detail": "No se puede crear un evento con fecha pasada."
}
```

</details>

---

## PF-03

**Consulta de catálogo y detalle de evento** · Requisito: RF-05 / CA-02 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Datos de ejemplo cargados. Sin sesión (consulta pública).
- **Resultado esperado:** 200 con datos reales y cupos coherentes.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Catálogo filtrado por tipo TALLER | (sin sesión) | `GET /api/eventos?tipo=TALLER` | 200 | 200 | ✅ 2 talleres |
| 2 | Detalle del evento 2 (Taller de Git) | (sin sesión) | `GET /api/eventos/2` | 200 | 200 | ✅ cupo=3 inscritos=2 disponibles=1 |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `GET /api/eventos?tipo=TALLER` → 200**

Respuesta:

```json
[
  {
    "id": 2,
    "titulo": "Taller de Git y GitHub",
    "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
    "tipo": "TALLER",
    "lugar": "Sala de cómputo 2",
    "fecha": "2026-11-21",
    "hora_inicio": "14:00:00",
    "hora_fin": "17:00:00",
    "cupo": 3,
    "fecha_limite_inscripcion": "2026-11-21",
    "estado": "PUBLICADO",
    "inscritos": 2,
    "cupos_disponibles": 1,
    "inscripciones_abiertas": true,
    "organizador": {
      "id": 2,
      "nombre": "Carlos Ruiz"
    }
  },
  {
    "id": 11,
    "titulo": "Taller de pruebas de software",
    "descripcion": "Evento creado durante las pruebas funcionales.",
    "tipo": "TALLER",
    "lugar": "Sala de cómputo 3",
    "fecha": "2026-12-08",
    "hora_inicio": "08:00:00",
    "hora_fin": "10:00:00",
    "cupo": 25,
    "fecha_limite_inscripcion": "2026-12-08",
    "est
  ... (respuesta recortada)
```

**Paso 2: `GET /api/eventos/2` → 200**

Respuesta:

```json
{
  "id": 2,
  "titulo": "Taller de Git y GitHub",
  "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 2",
  "fecha": "2026-11-21",
  "hora_inicio": "14:00:00",
  "hora_fin": "17:00:00",
  "cupo": 3,
  "fecha_limite_inscripcion": "2026-11-21",
  "estado": "PUBLICADO",
  "inscritos": 2,
  "cupos_disponibles": 1,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

</details>

---

## PF-04

**Consulta de evento inexistente** · Requisito: RF-05, RNF-03 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Sin sesión.
- **Resultado esperado:** 404 con mensaje controlado (sin detalles internos).

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Evento 99999 | (sin sesión) | `GET /api/eventos/99999` | 404 | 404 | ✅  |
| 2 | Evento en borrador (no público) | (sin sesión) | `GET /api/eventos/6` | 404 | 404 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `GET /api/eventos/99999` → 404**

Respuesta:

```json
{
  "detail": "El evento no existe."
}
```

**Paso 2: `GET /api/eventos/6` → 404**

Respuesta:

```json
{
  "detail": "El evento no existe."
}
```

</details>

---

## PF-05

**Inscripción válida de un participante** · Requisito: RF-06, RF-07 / CA-03 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Estudiante3 con sesión. Taller de Git (id 2) con cupo 3 y 2 inscritos.
- **Resultado esperado:** 201 y la inscripción aparece en «mis inscripciones».

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Inscribirse en el evento 2 | estudiante3 | `POST /api/eventos/2/inscripciones` | 201 | 201 | ✅  |
| 2 | Consultar mis inscripciones | estudiante3 | `GET /api/inscripciones/mias` | 200 | 200 | ✅ inscripción ACTIVA encontrada |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/2/inscripciones` → 201**

Respuesta:

```json
{
  "id": 24,
  "estado": "ACTIVA",
  "creada_en": "2026-11-18T11:08:32.151130",
  "cancelada_en": null,
  "evento": {
    "id": 2,
    "titulo": "Taller de Git y GitHub",
    "tipo": "TALLER",
    "fecha": "2026-11-21",
    "hora_inicio": "14:00:00",
    "hora_fin": "17:00:00",
    "lugar": "Sala de cómputo 2",
    "estado": "PUBLICADO"
  },
  "asistencia": null
}
```

**Paso 2: `GET /api/inscripciones/mias` → 200**

Respuesta:

```json
[
  {
    "id": 24,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:08:32.151130",
    "cancelada_en": null,
    "evento": {
      "id": 2,
      "titulo": "Taller de Git y GitHub",
      "tipo": "TALLER",
      "fecha": "2026-11-21",
      "hora_inicio": "14:00:00",
      "hora_fin": "17:00:00",
      "lugar": "Sala de cómputo 2",
      "estado": "PUBLICADO"
    },
    "asistencia": null
  },
  {
    "id": 3,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:07:07.364768",
    "cancelada_en": null,
    "evento": {
      "id": 1,
      "titulo": "Conferencia: Inteligencia artificial en la educación",
      "tipo": "CONFERENCIA",
      "fecha": "2026-11-18",
      "hora_inicio": "07:00:00",
      "hora_fin": "09:00:00",
      "lugar": "Auditorio principal",
      "estado": "PUBLICADO"
    },
    "asistencia": null
  },
  {
    "id": 21,
    "estado": "ACTIVA",
    "creada_en
  ... (respuesta recortada)
```

</details>

---

## PF-06

**Inscripción con datos inválidos** · Requisito: RF-01, RF-06, RNF-02 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Estudiante1 con sesión.
- **Resultado esperado:** 422/404 controlados; nada se guarda.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Identificador de evento no numérico | estudiante1 | `POST /api/eventos/abc/inscripciones` | 422 | 422 | ✅  |
| 2 | Evento en borrador | estudiante1 | `POST /api/eventos/6/inscripciones` | 404 | 404 | ✅  |
| 3 | Registro de cuenta con correo externo | (sin sesión) | `POST /api/auth/registro` | 422 | 422 | ✅  |
| 4 | Registro con documento con letras y clave corta | (sin sesión) | `POST /api/auth/registro` | 422 | 422 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/abc/inscripciones` → 422**

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "evento_id: Input should be a valid integer, unable to parse string as an integer"
  ]
}
```

**Paso 2: `POST /api/eventos/6/inscripciones` → 404**

Respuesta:

```json
{
  "detail": "El evento no existe."
}
```

**Paso 3: `POST /api/auth/registro` → 422**

Datos enviados:

```json
{
  "documento": "9999999",
  "nombre": "Persona Externa",
  "correo": "externo@gmail.com",
  "clave": "Clave123*"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "correo: Solo se permiten correos institucionales (@institucion.edu.co)."
  ]
}
```

**Paso 4: `POST /api/auth/registro` → 422**

Datos enviados:

```json
{
  "documento": "ABC",
  "nombre": "X",
  "correo": "nuevo@institucion.edu.co",
  "clave": "123"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "documento: String should have at least 5 characters",
    "nombre: String should have at least 3 characters",
    "clave: String should have at least 8 characters"
  ]
}
```

</details>

---

## PF-07

**Intento de inscripción con cupo agotado** · Requisito: RF-08 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Evento 2 con 3/3 inscritos tras PF-05. Estudiante4 con sesión.
- **Resultado esperado:** 409 «cupo agotado» y el número de inscritos no cambia.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Estudiante4 intenta inscribirse | estudiante4 | `POST /api/eventos/2/inscripciones` | 409 | 409 | ✅  |
| 2 | Verificar que el cupo se conservó | (sin sesión) | `GET /api/eventos/2` | 200 | 200 | ✅ inscritos=3 disponibles=0 |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/2/inscripciones` → 409**

Respuesta:

```json
{
  "detail": "El cupo del evento está agotado."
}
```

**Paso 2: `GET /api/eventos/2` → 200**

Respuesta:

```json
{
  "id": 2,
  "titulo": "Taller de Git y GitHub",
  "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 2",
  "fecha": "2026-11-21",
  "hora_inicio": "14:00:00",
  "hora_fin": "17:00:00",
  "cupo": 3,
  "fecha_limite_inscripcion": "2026-11-21",
  "estado": "PUBLICADO",
  "inscritos": 3,
  "cupos_disponibles": 0,
  "inscripciones_abiertas": false,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

</details>

---

## PF-08

**Intento de inscripción duplicada** · Requisito: RF-09 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Estudiante1 ya inscrito en el evento 1.
- **Resultado esperado:** 409 «ya está inscrito».

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Estudiante1 se inscribe otra vez en el evento 1 | estudiante1 | `POST /api/eventos/1/inscripciones` | 409 | 409 | ✅  |
| 2 | Verificar que no hay registros repetidos | estudiante1 | `GET /api/inscripciones/mias` | 200 | 200 | ✅ una sola inscripción al evento 1 |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/1/inscripciones` → 409**

Respuesta:

```json
{
  "detail": "Ya está inscrito en este evento."
}
```

**Paso 2: `GET /api/inscripciones/mias` → 200**

Respuesta:

```json
[
  {
    "id": 5,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:07:07.365940",
    "cancelada_en": null,
    "evento": {
      "id": 2,
      "titulo": "Taller de Git y GitHub",
      "tipo": "TALLER",
      "fecha": "2026-11-21",
      "hora_inicio": "14:00:00",
      "hora_fin": "17:00:00",
      "lugar": "Sala de cómputo 2",
      "estado": "PUBLICADO"
    },
    "asistencia": null
  },
  {
    "id": 1,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:07:07.364763",
    "cancelada_en": null,
    "evento": {
      "id": 1,
      "titulo": "Conferencia: Inteligencia artificial en la educación",
      "tipo": "CONFERENCIA",
      "fecha": "2026-11-18",
      "hora_inicio": "07:00:00",
      "hora_fin": "09:00:00",
      "lugar": "Auditorio principal",
      "estado": "PUBLICADO"
    },
    "asistencia": null
  },
  {
    "id": 14,
    "estado": "ACTIVA",
    "creada_en"
  ... (respuesta recortada)
```

</details>

---

## PF-09

**Gestión de evento o asistencia sin autorización** · Requisito: RF-02, RNF-01 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Varias sesiones con roles distintos.
- **Resultado esperado:** 401 sin sesión y 403 con rol o dueño incorrecto.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Crear evento sin iniciar sesión | (sin sesión) | `POST /api/eventos` | 401 | 401 | ✅  |
| 2 | Participante intenta crear evento | estudiante1 | `POST /api/eventos` | 403 | 403 | ✅  |
| 3 | Organizador2 intenta cancelar evento de Organizador1 | organizador2 | `PATCH /api/eventos/1/cancelar` | 403 | 403 | ✅  |
| 4 | Participante intenta registrar asistencia | estudiante1 | `PUT /api/eventos/1/asistencia/1` | 403 | 403 | ✅  |
| 5 | Organizador intenta ver reportes de coordinación | organizador1 | `GET /api/reportes/eventos` | 403 | 403 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos` → 401**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08"
}
```

Respuesta:

```json
{
  "detail": "Debe iniciar sesión."
}
```

**Paso 2: `POST /api/eventos` → 403**

Datos enviados:

```json
{
  "titulo": "Taller de pruebas de software",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-12-08",
  "hora_inicio": "08:00",
  "hora_fin": "10:00",
  "cupo": 25,
  "fecha_limite_inscripcion": "2026-12-08"
}
```

Respuesta:

```json
{
  "detail": "No tiene permiso para realizar esta acción."
}
```

**Paso 3: `PATCH /api/eventos/1/cancelar` → 403**

Respuesta:

```json
{
  "detail": "Solo el organizador del evento o la coordinación pueden gestionarlo."
}
```

**Paso 4: `PUT /api/eventos/1/asistencia/1` → 403**

Datos enviados:

```json
{
  "estado": "ASISTIO"
}
```

Respuesta:

```json
{
  "detail": "No tiene permiso para realizar esta acción."
}
```

**Paso 5: `GET /api/reportes/eventos` → 403**

Respuesta:

```json
{
  "detail": "No tiene permiso para realizar esta acción."
}
```

</details>

---

## PF-10

**Registro y consulta de asistencia** · Requisito: RF-11, RF-12 / CA-05 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Evento 1 se realiza hoy, con 4 inscritos. Organizador1 con sesión.
- **Resultado esperado:** 201 al registrar, la lista muestra la asistencia asociada a evento y participante.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Consultar lista de participantes del evento 1 | organizador1 | `GET /api/eventos/1/participantes` | 200 | 200 | ✅  |
| 2 | Registrar ASISTIO | organizador1 | `PUT /api/eventos/1/asistencia/1` | 201 | 201 | ✅  |
| 3 | Consultar lista actualizada | organizador1 | `GET /api/eventos/1/participantes` | 200 | 200 | ✅ asistencia ASISTIO guardada |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `GET /api/eventos/1/participantes` → 200**

Respuesta:

```json
{
  "evento": {
    "id": 1,
    "titulo": "Conferencia: Inteligencia artificial en la educación",
    "descripcion": "Conferencia: Inteligencia artificial en la educación. Actividad académica abierta a la comunidad institucional.",
    "tipo": "CONFERENCIA",
    "lugar": "Auditorio principal",
    "fecha": "2026-11-18",
    "hora_inicio": "07:00:00",
    "hora_fin": "09:00:00",
    "cupo": 30,
    "fecha_limite_inscripcion": "2026-11-18",
    "estado": "PUBLICADO",
    "inscritos": 4,
    "cupos_disponibles": 26,
    "inscripciones_abiertas": true,
    "organizador": {
      "id": 2,
      "nombre": "Carlos Ruiz"
    }
  },
  "participantes": [
    {
      "inscripcion_id": 1,
      "participante_id": 4,
      "documento": "2000000001",
      "nombre": "Ana Torres",
      "correo": "estudiante1@institucion.edu.co",
      "estado_inscripcion": "ACTIVA",
      "asistencia": null,
      "a
  ... (respuesta recortada)
```

**Paso 2: `PUT /api/eventos/1/asistencia/1` → 201**

Datos enviados:

```json
{
  "estado": "ASISTIO"
}
```

Respuesta:

```json
{
  "inscripcion_id": 1,
  "participante_id": 4,
  "documento": "2000000001",
  "nombre": "Ana Torres",
  "correo": "estudiante1@institucion.edu.co",
  "estado_inscripcion": "ACTIVA",
  "asistencia": "ASISTIO",
  "asistencia_registrada_en": "2026-11-18T11:08:32.227254"
}
```

**Paso 3: `GET /api/eventos/1/participantes` → 200**

Respuesta:

```json
{
  "evento": {
    "id": 1,
    "titulo": "Conferencia: Inteligencia artificial en la educación",
    "descripcion": "Conferencia: Inteligencia artificial en la educación. Actividad académica abierta a la comunidad institucional.",
    "tipo": "CONFERENCIA",
    "lugar": "Auditorio principal",
    "fecha": "2026-11-18",
    "hora_inicio": "07:00:00",
    "hora_fin": "09:00:00",
    "cupo": 30,
    "fecha_limite_inscripcion": "2026-11-18",
    "estado": "PUBLICADO",
    "inscritos": 4,
    "cupos_disponibles": 26,
    "inscripciones_abiertas": true,
    "organizador": {
      "id": 2,
      "nombre": "Carlos Ruiz"
    }
  },
  "participantes": [
    {
      "inscripcion_id": 1,
      "participante_id": 4,
      "documento": "2000000001",
      "nombre": "Ana Torres",
      "correo": "estudiante1@institucion.edu.co",
      "estado_inscripcion": "ACTIVA",
      "asistencia": "ASISTIO",
   
  ... (respuesta recortada)
```

</details>

---

## PF-11

**Información consolidada y consistencia de datos** · Requisito: RF-13, RF-14 / CA-06 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Coordinación con sesión.
- **Resultado esperado:** Para cada actividad: inscritos + disponibles = cupo y asistieron + no asistieron + sin registro = inscritos; coincide con el catálogo.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Reporte por actividad | coordinacion | `GET /api/reportes/eventos` | 200 | 200 | ✅  |
| 2 | Reporte por periodo (mes) | coordinacion | `GET /api/reportes/periodos` | 200 | 200 | ✅ 2 periodos |

**Verificaciones adicionales:**

- ✅ 10 actividades revisadas: totales coherentes
- ✅ Evento 2: catálogo=3 inscritos, reporte=3 inscritos

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `GET /api/reportes/eventos` → 200**

Respuesta:

```json
[
  {
    "evento_id": 7,
    "titulo": "Taller de Python básico",
    "tipo": "TALLER",
    "fecha": "2026-10-09",
    "estado": "PUBLICADO",
    "organizador": "Carlos Ruiz",
    "cupo": 20,
    "inscritos": 5,
    "cupos_disponibles": 15,
    "asistieron": 4,
    "no_asistieron": 1,
    "sin_registro": 0,
    "porcentaje_asistencia": 80.0
  },
  {
    "evento_id": 8,
    "titulo": "Conferencia de ciberseguridad",
    "tipo": "CONFERENCIA",
    "fecha": "2026-10-14",
    "estado": "PUBLICADO",
    "organizador": "Marta Díaz",
    "cupo": 50,
    "inscritos": 6,
    "cupos_disponibles": 44,
    "asistieron": 4,
    "no_asistieron": 2,
    "sin_registro": 0,
    "porcentaje_asistencia": 66.7
  },
  {
    "evento_id": 9,
    "titulo": "Taller de fotografía digital",
    "tipo": "TALLER",
    "fecha": "2026-10-29",
    "estado": "CANCELADO",
    "organizador": "Marta Díaz",
    "cupo": 15,
  ... (respuesta recortada)
```

**Paso 2: `GET /api/reportes/periodos` → 200**

Respuesta:

```json
[
  {
    "periodo": "2026-10",
    "eventos": 2,
    "cupo_total": 70,
    "inscritos": 11,
    "asistieron": 8,
    "porcentaje_asistencia": 72.7
  },
  {
    "periodo": "2026-11",
    "eventos": 2,
    "cupo_total": 45,
    "inscritos": 8,
    "asistieron": 4,
    "porcentaje_asistencia": 50.0
  }
]
```

</details>

---

## PF-12

**Integración: flujo completo creación → inscripción → asistencia** · Requisito: CA-01 a CA-06 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Servidor y base de datos en ejecución.
- **Resultado esperado:** Cada paso queda persistido y se refleja en los siguientes.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Organizador1 crea evento para hoy | organizador1 | `POST /api/eventos` | 201 | 201 | ✅  |
| 2 | Publicar | organizador1 | `PATCH /api/eventos/12/publicar` | 200 | 200 | ✅  |
| 3 | Estudiante5 se inscribe | estudiante5 | `POST /api/eventos/12/inscripciones` | 201 | 201 | ✅  |
| 4 | Catálogo refleja 1 inscrito y 4 disponibles | (sin sesión) | `GET /api/eventos/12` | 200 | 200 | ✅ inscritos=1 |
| 5 | Organizador1 registra asistencia | organizador1 | `PUT /api/eventos/12/asistencia/25` | 201 | 201 | ✅  |
| 6 | Coordinación ve 100 % de asistencia en el reporte | coordinacion | `GET /api/reportes/eventos` | 200 | 200 | ✅ 100 % en el reporte |
| 7 | El participante ve su asistencia | estudiante5 | `GET /api/inscripciones/mias` | 200 | 200 | ✅ asistencia visible para el participante |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos` → 201**

Datos enviados:

```json
{
  "titulo": "Charla de integración",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-11-18",
  "hora_inicio": "23:00",
  "hora_fin": "23:59",
  "cupo": 5,
  "fecha_limite_inscripcion": "2026-11-18"
}
```

Respuesta:

```json
{
  "id": 12,
  "titulo": "Charla de integración",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-11-18",
  "hora_inicio": "23:00:00",
  "hora_fin": "23:59:00",
  "cupo": 5,
  "fecha_limite_inscripcion": "2026-11-18",
  "estado": "BORRADOR",
  "inscritos": 0,
  "cupos_disponibles": 5,
  "inscripciones_abiertas": false,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 2: `PATCH /api/eventos/12/publicar` → 200**

Respuesta:

```json
{
  "id": 12,
  "titulo": "Charla de integración",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-11-18",
  "hora_inicio": "23:00:00",
  "hora_fin": "23:59:00",
  "cupo": 5,
  "fecha_limite_inscripcion": "2026-11-18",
  "estado": "PUBLICADO",
  "inscritos": 0,
  "cupos_disponibles": 5,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 3: `POST /api/eventos/12/inscripciones` → 201**

Respuesta:

```json
{
  "id": 25,
  "estado": "ACTIVA",
  "creada_en": "2026-11-18T11:08:32.296912",
  "cancelada_en": null,
  "evento": {
    "id": 12,
    "titulo": "Charla de integración",
    "tipo": "TALLER",
    "fecha": "2026-11-18",
    "hora_inicio": "23:00:00",
    "hora_fin": "23:59:00",
    "lugar": "Sala de cómputo 3",
    "estado": "PUBLICADO"
  },
  "asistencia": null
}
```

**Paso 4: `GET /api/eventos/12` → 200**

Respuesta:

```json
{
  "id": 12,
  "titulo": "Charla de integración",
  "descripcion": "Evento creado durante las pruebas funcionales.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 3",
  "fecha": "2026-11-18",
  "hora_inicio": "23:00:00",
  "hora_fin": "23:59:00",
  "cupo": 5,
  "fecha_limite_inscripcion": "2026-11-18",
  "estado": "PUBLICADO",
  "inscritos": 1,
  "cupos_disponibles": 4,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 5: `PUT /api/eventos/12/asistencia/25` → 201**

Datos enviados:

```json
{
  "estado": "ASISTIO"
}
```

Respuesta:

```json
{
  "inscripcion_id": 25,
  "participante_id": 8,
  "documento": "2000000005",
  "nombre": "Elena Vargas",
  "correo": "estudiante5@institucion.edu.co",
  "estado_inscripcion": "ACTIVA",
  "asistencia": "ASISTIO",
  "asistencia_registrada_en": "2026-11-18T11:08:32.322018"
}
```

**Paso 6: `GET /api/reportes/eventos` → 200**

Respuesta:

```json
[
  {
    "evento_id": 7,
    "titulo": "Taller de Python básico",
    "tipo": "TALLER",
    "fecha": "2026-10-09",
    "estado": "PUBLICADO",
    "organizador": "Carlos Ruiz",
    "cupo": 20,
    "inscritos": 5,
    "cupos_disponibles": 15,
    "asistieron": 4,
    "no_asistieron": 1,
    "sin_registro": 0,
    "porcentaje_asistencia": 80.0
  },
  {
    "evento_id": 8,
    "titulo": "Conferencia de ciberseguridad",
    "tipo": "CONFERENCIA",
    "fecha": "2026-10-14",
    "estado": "PUBLICADO",
    "organizador": "Marta Díaz",
    "cupo": 50,
    "inscritos": 6,
    "cupos_disponibles": 44,
    "asistieron": 4,
    "no_asistieron": 2,
    "sin_registro": 0,
    "porcentaje_asistencia": 66.7
  },
  {
    "evento_id": 9,
    "titulo": "Taller de fotografía digital",
    "tipo": "TALLER",
    "fecha": "2026-10-29",
    "estado": "CANCELADO",
    "organizador": "Marta Díaz",
    "cupo": 15,
  ... (respuesta recortada)
```

**Paso 7: `GET /api/inscripciones/mias` → 200**

Respuesta:

```json
[
  {
    "id": 8,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:07:07.367049",
    "cancelada_en": null,
    "evento": {
      "id": 5,
      "titulo": "Conferencia de emprendimiento",
      "tipo": "CONFERENCIA",
      "fecha": "2026-11-25",
      "hora_inicio": "10:00:00",
      "hora_fin": "12:00:00",
      "lugar": "Auditorio principal",
      "estado": "PUBLICADO"
    },
    "asistencia": null
  },
  {
    "id": 25,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:08:32.296912",
    "cancelada_en": null,
    "evento": {
      "id": 12,
      "titulo": "Charla de integración",
      "tipo": "TALLER",
      "fecha": "2026-11-18",
      "hora_inicio": "23:00:00",
      "hora_fin": "23:59:00",
      "lugar": "Sala de cómputo 3",
      "estado": "PUBLICADO"
    },
    "asistencia": "ASISTIO"
  },
  {
    "id": 22,
    "estado": "ACTIVA",
    "creada_en": "2026-11-18T11:
  ... (respuesta recortada)
```

</details>

---

## PF-13

**Cruce de horario entre actividades** · Requisito: RF-10 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Estudiante1 inscrito en Taller de Git (id 2, 14:00-17:00). Seminario de BD (id 3) mismo día 15:00-16:00.
- **Resultado esperado:** 409 por cruce de horario.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Inscribirse en el evento 3 | estudiante1 | `POST /api/eventos/3/inscripciones` | 409 | 409 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/3/inscripciones` → 409**

Respuesta:

```json
{
  "detail": "Ya está inscrito en «Taller de Git y GitHub» en un horario que se cruza con este evento."
}
```

</details>

---

## PF-14

**Inscripción después de la fecha límite** · Requisito: RF-08 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Capacitación en primeros auxilios (id 4) con fecha límite ayer.
- **Resultado esperado:** 409 fecha límite vencida.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Estudiante1 intenta inscribirse | estudiante1 | `POST /api/eventos/4/inscripciones` | 409 | 409 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/eventos/4/inscripciones` → 409**

Respuesta:

```json
{
  "detail": "La fecha límite de inscripción ya pasó."
}
```

</details>

---

## PF-15

**Cancelar inscripción libera el cupo** · Requisito: RF-07 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Evento 2 lleno (3/3). Estudiante3 inscrito.
- **Resultado esperado:** 200 al cancelar, el cupo vuelve a 1 y Estudiante4 puede inscribirse.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Estudiante3 cancela su inscripción | estudiante3 | `PATCH /api/inscripciones/24/cancelar` | 200 | 200 | ✅  |
| 2 | Cupo disponible otra vez | (sin sesión) | `GET /api/eventos/2` | 200 | 200 | ✅ disponibles=1 |
| 3 | Estudiante4 ahora sí se inscribe | estudiante4 | `POST /api/eventos/2/inscripciones` | 201 | 201 | ✅  |
| 4 | Estudiante4 intenta cancelar inscripción ajena | estudiante4 | `PATCH /api/inscripciones/1/cancelar` | 403 | 403 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `PATCH /api/inscripciones/24/cancelar` → 200**

Respuesta:

```json
{
  "id": 24,
  "estado": "CANCELADA",
  "creada_en": "2026-11-18T11:08:32.151130",
  "cancelada_en": "2026-11-18T11:08:32.380971",
  "evento": {
    "id": 2,
    "titulo": "Taller de Git y GitHub",
    "tipo": "TALLER",
    "fecha": "2026-11-21",
    "hora_inicio": "14:00:00",
    "hora_fin": "17:00:00",
    "lugar": "Sala de cómputo 2",
    "estado": "PUBLICADO"
  },
  "asistencia": null
}
```

**Paso 2: `GET /api/eventos/2` → 200**

Respuesta:

```json
{
  "id": 2,
  "titulo": "Taller de Git y GitHub",
  "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 2",
  "fecha": "2026-11-21",
  "hora_inicio": "14:00:00",
  "hora_fin": "17:00:00",
  "cupo": 3,
  "fecha_limite_inscripcion": "2026-11-21",
  "estado": "PUBLICADO",
  "inscritos": 2,
  "cupos_disponibles": 1,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 2,
    "nombre": "Carlos Ruiz"
  }
}
```

**Paso 3: `POST /api/eventos/2/inscripciones` → 201**

Respuesta:

```json
{
  "id": 26,
  "estado": "ACTIVA",
  "creada_en": "2026-11-18T11:08:32.396990",
  "cancelada_en": null,
  "evento": {
    "id": 2,
    "titulo": "Taller de Git y GitHub",
    "tipo": "TALLER",
    "fecha": "2026-11-21",
    "hora_inicio": "14:00:00",
    "hora_fin": "17:00:00",
    "lugar": "Sala de cómputo 2",
    "estado": "PUBLICADO"
  },
  "asistencia": null
}
```

**Paso 4: `PATCH /api/inscripciones/1/cancelar` → 403**

Respuesta:

```json
{
  "detail": "Solo puede cancelar sus propias inscripciones."
}
```

</details>

---

## PF-16

**Asistencia fuera de las reglas** · Requisito: RF-11 / CA-05 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Organizador1 con sesión.
- **Resultado esperado:** 404 para quien no está inscrito en el evento; 409 si el evento no es hoy.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Registrar asistencia con inscripción de otro evento | organizador1 | `PUT /api/eventos/1/asistencia/5` | 404 | 404 | ✅  |
| 2 | Registrar asistencia antes del día del evento (evento 2) | organizador1 | `PUT /api/eventos/2/asistencia/5` | 409 | 409 | ✅  |
| 3 | Estado de asistencia inválido | organizador1 | `PUT /api/eventos/1/asistencia/1` | 422 | 422 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `PUT /api/eventos/1/asistencia/5` → 404**

Datos enviados:

```json
{
  "estado": "ASISTIO"
}
```

Respuesta:

```json
{
  "detail": "La persona no tiene inscripción en este evento."
}
```

**Paso 2: `PUT /api/eventos/2/asistencia/5` → 409**

Datos enviados:

```json
{
  "estado": "ASISTIO"
}
```

Respuesta:

```json
{
  "detail": "La asistencia se registra el día del evento (2026-11-21)."
}
```

**Paso 3: `PUT /api/eventos/1/asistencia/1` → 422**

Datos enviados:

```json
{
  "estado": "TARDE"
}
```

Respuesta:

```json
{
  "detail": "Datos inválidos",
  "errores": [
    "estado: Input should be 'ASISTIO' or 'NO_ASISTIO'"
  ]
}
```

</details>

---

## PF-17

**Corrección de asistencia** · Requisito: RF-12 / CA-05 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Asistencia registrada en PF-10.
- **Resultado esperado:** 200 y el estado cambia a NO_ASISTIO.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Corregir a NO_ASISTIO | organizador1 | `PUT /api/eventos/1/asistencia/1` | 200 | 200 | ✅ asistencia=NO_ASISTIO |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `PUT /api/eventos/1/asistencia/1` → 200**

Datos enviados:

```json
{
  "estado": "NO_ASISTIO"
}
```

Respuesta:

```json
{
  "inscripcion_id": 1,
  "participante_id": 4,
  "documento": "2000000001",
  "nombre": "Ana Torres",
  "correo": "estudiante1@institucion.edu.co",
  "estado_inscripcion": "ACTIVA",
  "asistencia": "NO_ASISTIO",
  "asistencia_registrada_en": "2026-11-18T11:08:32.435531"
}
```

</details>

---

## PF-18

**No se puede reducir el cupo por debajo de los inscritos** · Requisito: RF-03 / CA-04 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Evento 2 con 3 inscritos.
- **Resultado esperado:** 409.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Cambiar cupo a 1 | organizador1 | `PUT /api/eventos/2` | 409 | 409 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `PUT /api/eventos/2` → 409**

Datos enviados:

```json
{
  "titulo": "Taller de Git y GitHub",
  "descripcion": "Taller de Git y GitHub. Actividad académica abierta a la comunidad institucional.",
  "tipo": "TALLER",
  "lugar": "Sala de cómputo 2",
  "fecha": "2026-11-21",
  "hora_inicio": "14:00:00",
  "hora_fin": "17:00:00",
  "fecha_limite_inscripcion": "2026-11-21",
  "cupo": 1
}
```

Respuesta:

```json
{
  "detail": "El cupo no puede ser menor que las personas ya inscritas (3)."
}
```

</details>

---

## PF-19

**Coordinación modifica y cancela eventos de cualquier organizador** · Requisito: RF-15 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Coordinación con sesión. Evento 5 de Organizador2.
- **Resultado esperado:** 200 al modificar y cancelar; el evento cancelado no admite inscripciones.

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Coordinación cambia el lugar | coordinacion | `PUT /api/eventos/5` | 200 | 200 | ✅ lugar actualizado |
| 2 | Coordinación cancela el evento | coordinacion | `PATCH /api/eventos/5/cancelar` | 200 | 200 | ✅  |
| 3 | Participante intenta inscribirse al cancelado | estudiante1 | `POST /api/eventos/5/inscripciones` | 409 | 409 | ✅  |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `PUT /api/eventos/5` → 200**

Datos enviados:

```json
{
  "titulo": "Conferencia de emprendimiento",
  "descripcion": "Conferencia de emprendimiento. Actividad académica abierta a la comunidad institucional.",
  "tipo": "CONFERENCIA",
  "lugar": "Auditorio norte",
  "fecha": "2026-11-25",
  "hora_inicio": "10:00:00",
  "hora_fin": "12:00:00",
  "fecha_limite_inscripcion": "2026-11-25",
  "cupo": 40
}
```

Respuesta:

```json
{
  "id": 5,
  "titulo": "Conferencia de emprendimiento",
  "descripcion": "Conferencia de emprendimiento. Actividad académica abierta a la comunidad institucional.",
  "tipo": "CONFERENCIA",
  "lugar": "Auditorio norte",
  "fecha": "2026-11-25",
  "hora_inicio": "10:00:00",
  "hora_fin": "12:00:00",
  "cupo": 40,
  "fecha_limite_inscripcion": "2026-11-25",
  "estado": "PUBLICADO",
  "inscritos": 2,
  "cupos_disponibles": 38,
  "inscripciones_abiertas": true,
  "organizador": {
    "id": 3,
    "nombre": "Marta Díaz"
  }
}
```

**Paso 2: `PATCH /api/eventos/5/cancelar` → 200**

Respuesta:

```json
{
  "id": 5,
  "titulo": "Conferencia de emprendimiento",
  "descripcion": "Conferencia de emprendimiento. Actividad académica abierta a la comunidad institucional.",
  "tipo": "CONFERENCIA",
  "lugar": "Auditorio norte",
  "fecha": "2026-11-25",
  "hora_inicio": "10:00:00",
  "hora_fin": "12:00:00",
  "cupo": 40,
  "fecha_limite_inscripcion": "2026-11-25",
  "estado": "CANCELADO",
  "inscritos": 2,
  "cupos_disponibles": 38,
  "inscripciones_abiertas": false,
  "organizador": {
    "id": 3,
    "nombre": "Marta Díaz"
  }
}
```

**Paso 3: `POST /api/eventos/5/inscripciones` → 409**

Respuesta:

```json
{
  "detail": "El evento fue cancelado; no admite inscripciones."
}
```

</details>

---

## PF-20

**Inicio de sesión** · Requisito: RF-01, RF-02, RNF-01 · Estado: ✅ Aprobada

- **Condiciones iniciales:** Cuentas de ejemplo.
- **Resultado esperado:** 200 con credenciales correctas; 401 con contraseña incorrecta (mensaje genérico).

| # | Paso | Usuario | Método y ruta | Código esperado | Código obtenido | Resultado |
|---|---|---|---|---|---|---|
| 1 | Contraseña incorrecta | (sin sesión) | `POST /api/auth/login` | 401 | 401 | ✅  |
| 2 | Credenciales correctas | (sin sesión) | `POST /api/auth/login` | 200 | 200 | ✅ rol PARTICIPANTE |

<details><summary>Ver solicitudes y respuestas</summary>

**Paso 1: `POST /api/auth/login` → 401**

Datos enviados:

```json
{
  "correo": "estudiante1@institucion.edu.co",
  "clave": "otra"
}
```

Respuesta:

```json
{
  "detail": "Correo o contraseña incorrectos."
}
```

**Paso 2: `POST /api/auth/login` → 200**

Datos enviados:

```json
{
  "correo": "estudiante1@institucion.edu.co",
  "clave": "Clave123*"
}
```

Respuesta:

```json
{
  "token": "aae704910314d0b2e3c3ab5464184e55b5b4f17305a710cb951b542e20a52510",
  "expira_en": "2026-11-18T19:08:32.565100",
  "usuario": {
    "id": 4,
    "documento": "2000000001",
    "nombre": "Ana Torres",
    "correo": "estudiante1@institucion.edu.co",
    "rol": "PARTICIPANTE"
  }
}
```

</details>

---

## Verificación directa en la base de datos

Después del flujo de integración (PF-12) se consultan las tablas de SQLite con SQL, sin usar la API, para comprobar que el evento, la inscripción y la asistencia quedaron guardados y relacionados.

**Evento creado en PF-12**

```sql
SELECT id, titulo, estado, fecha, cupo FROM eventos WHERE id = 12
```

| id | titulo | estado | fecha | cupo |
|---|---|---|---|---|
| 12 | Charla de integración | PUBLICADO | 2026-11-18 | 5 |

**Inscripciones del evento**

```sql
SELECT i.id, u.nombre, u.correo, i.estado FROM inscripciones i JOIN usuarios u ON u.id = i.participante_id WHERE i.evento_id = 12
```

| id | nombre | correo | estado |
|---|---|---|---|
| 25 | Elena Vargas | estudiante5@institucion.edu.co | ACTIVA |

**Asistencia registrada**

```sql
SELECT a.id, a.inscripcion_id, u.nombre, a.estado FROM asistencias a JOIN inscripciones i ON i.id = a.inscripcion_id JOIN usuarios u ON u.id = i.participante_id WHERE i.evento_id = 12
```

| id | inscripcion_id | nombre | estado |
|---|---|---|---|
| 17 | 25 | Elena Vargas | ASISTIO |
