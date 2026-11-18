# Matriz de trazabilidad

Relaciona cada condición de aceptación obligatoria con los requisitos aprobados, el código que la implementa, el pull request donde se integró y la prueba que la verifica.

> Los números de pull request corresponden al repositorio en GitHub (pestaña *Pull requests → Closed*).

| Condición | Requisito aprobado | Implementación (ruta / componente) | Pull request | Prueba |
|---|---|---|---|---|
| **CA-01** Crear y publicar actividades | RF-03, RF-04, RF-15 · RN-12, RN-16 | `POST /api/eventos`, `PUT /api/eventos/{id}`, `PATCH /api/eventos/{id}/publicar`, `PATCH /api/eventos/{id}/cancelar` · `backend/app/routers/eventos.py` · `frontend/gestion.html` | #3 (modelo), #4 (API), #8 (interfaz) | PF-01, PF-02, PF-12, PF-18, PF-19, IU-02 |
| **CA-02** Consultar eventos y disponibilidad | RF-05 · RN-02 | `GET /api/eventos`, `GET /api/eventos/{id}` · `routers/eventos.py` · `frontend/index.html` | #4 (API), #7 (interfaz) | PF-03, PF-04, IU-03 |
| **CA-03** Inscribirse en una actividad | RF-01, RF-06, RF-07 · RN-01 | `POST /api/auth/registro`, `POST /api/eventos/{id}/inscripciones`, `GET /api/inscripciones/mias` · `routers/auth.py`, `routers/inscripciones.py` · `frontend/login.html`, `index.html`, `mis-inscripciones.html` | #3 (auth), #5 (API), #7 (interfaz) | PF-05, PF-06, PF-12, IU-03 |
| **CA-04** Administrar cupos e impedir inscripciones incompatibles | RF-07, RF-08, RF-09, RF-10 · RN-03 a RN-07, RN-12 | `inscribirse()` y `cancelar_inscripcion()` en `routers/inscripciones.py` · restricción `UNIQUE(evento_id, participante_id)` en `models.py` | #3 (restricciones), #5 (reglas) | PF-07, PF-08, PF-13, PF-14, PF-15, PF-18, IU-04 |
| **CA-05** Registrar asistencia y consultar lista | RF-11, RF-12 · RN-08 a RN-11 | `GET /api/eventos/{id}/participantes`, `PUT /api/eventos/{id}/asistencia/{inscripcion_id}` · `routers/asistencia.py` · tabla `asistencias` · `frontend/asistencia.html` | #3 (modelo), #6 (API), #8 (interfaz) | PF-10, PF-16, PF-17, PF-12, IU-05 |
| **CA-06** Información consolidada para coordinación | RF-13, RF-14 | `GET /api/reportes/eventos`, `GET /api/reportes/periodos` · `routers/reportes.py` · `frontend/reportes.html` | #6 (API), #8 (interfaz) | PF-11, PF-12, IU-06 |

## Requisitos transversales

| Requisito | Implementación | Pull request | Prueba |
|---|---|---|---|
| RF-02 / RNF-01 Sesiones y permisos por rol | `security.py` (`requiere_rol`, sesiones con token), `verificar_permiso_gestion` en `routers/eventos.py`, `js/api.js` (menú por rol) | #3, #4, #7 | PF-09, PF-20, IU-01, IU-07 |
| RNF-02 Validación en el servidor | `schemas.py` | #3 | PF-02, PF-06, PF-16 |
| RNF-03 Manejo de errores | Manejadores de error en `main.py` | #3 | PF-04, PF-06 |
| RNF-04 Persistencia | `models.py`, `database.py` (SQLite) | #3 | PF-12, IU-08 |
| RNF-06 Instalación reproducible | `README.md`, `requirements.txt`, `.env.example`, `seed.py` | #1, #10 | Instalación desde cero |
