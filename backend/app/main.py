"""Punto de entrada de la aplicación.

- Crea las tablas de la base de datos (y carga datos de ejemplo si está vacía).
- Registra automáticamente todos los servicios que existan en la carpeta routers/.
- Sirve la interfaz web (carpeta frontend/) en la raíz del sitio.
"""
import importlib
import logging
import pkgutil
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import routers
from .database import Base, engine

log = logging.getLogger("eventos")

CARPETA_FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI):
    Base.metadata.create_all(engine)
    try:
        from .seed import cargar_si_esta_vacia

        cargar_si_esta_vacia()
    except ImportError:
        pass  # Los datos de ejemplo son opcionales.
    yield


app = FastAPI(
    title="API Eventos Académicos",
    description="Organización de eventos y actividades académicas: eventos, inscripciones, cupos y asistencia.",
    version="1.0.0",
    lifespan=ciclo_de_vida,
)


# ---------- Manejo de errores ----------
@app.exception_handler(RequestValidationError)
async def error_de_validacion(_request: Request, exc: RequestValidationError):
    """Devuelve los errores de validación con mensajes claros (código 422)."""
    mensajes = []
    for error in exc.errors():
        campo = ".".join(str(p) for p in error["loc"] if p not in ("body", "query", "path"))
        mensaje = error["msg"].removeprefix("Value error, ")
        mensajes.append(f"{campo}: {mensaje}" if campo else mensaje)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Datos inválidos", "errores": mensajes},
    )


@app.exception_handler(Exception)
async def error_inesperado(_request: Request, exc: Exception):
    """Evita mostrar detalles internos (información sensible) al usuario."""
    log.exception("Error no controlado: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocurrió un error interno. Intente de nuevo más tarde."},
    )


@app.get("/api/salud", tags=["Sistema"])
def salud():
    return {"estado": "ok"}


# ---------- Registro automático de servicios (routers) ----------
for modulo in pkgutil.iter_modules(routers.__path__):
    router = getattr(importlib.import_module(f"{routers.__name__}.{modulo.name}"), "router", None)
    if router is not None:
        app.include_router(router)


# ---------- Interfaz web ----------
if CARPETA_FRONTEND.exists():
    app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
