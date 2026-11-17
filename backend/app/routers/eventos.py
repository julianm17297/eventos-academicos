"""Servicios de eventos: catálogo público, creación, edición, publicación y cancelación."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import obtener_db
from ..models import Evento, Usuario
from ..schemas import EventoEntrada, EventoSalida, TipoEvento
from ..security import requiere_rol

router = APIRouter(tags=["Eventos"])

gestor = requiere_rol("ORGANIZADOR", "COORDINACION")


# ---------- Funciones de apoyo (reglas de negocio de eventos) ----------
def inscripciones_abiertas(evento: Evento) -> bool:
    return (
        evento.estado == "PUBLICADO"
        and date.today() <= evento.fecha_limite_inscripcion
        and evento.cupos_disponibles > 0
    )


def a_salida(evento: Evento) -> EventoSalida:
    salida = EventoSalida.model_validate(evento)
    salida.inscripciones_abiertas = inscripciones_abiertas(evento)
    return salida


def buscar_evento(db: Session, evento_id: int) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El evento no existe.")
    return evento


def verificar_permiso_gestion(usuario: Usuario, evento: Evento) -> None:
    """Coordinación gestiona todos los eventos; un organizador solo los suyos."""
    if usuario.rol == "COORDINACION":
        return
    if usuario.rol == "ORGANIZADOR" and evento.organizador_id == usuario.id:
        return
    raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo el organizador del evento o la coordinación pueden gestionarlo.")


# ---------- Catálogo público ----------
@router.get("/api/eventos", response_model=list[EventoSalida])
def catalogo(
    tipo: TipoEvento | None = None,
    incluir_pasados: bool = Query(False, description="Incluir eventos con fecha anterior a hoy"),
    db: Session = Depends(obtener_db),
):
    """Eventos publicados (y cancelados, para que los inscritos se enteren)."""
    consulta = select(Evento).where(Evento.estado.in_(["PUBLICADO", "CANCELADO"]))
    if tipo:
        consulta = consulta.where(Evento.tipo == tipo)
    if not incluir_pasados:
        consulta = consulta.where(Evento.fecha >= date.today())
    eventos = db.scalars(consulta.order_by(Evento.fecha, Evento.hora_inicio)).all()
    return [a_salida(e) for e in eventos]


@router.get("/api/eventos/{evento_id}", response_model=EventoSalida)
def detalle_evento(evento_id: int, db: Session = Depends(obtener_db)):
    evento = buscar_evento(db, evento_id)
    if evento.estado == "BORRADOR":
        # Un borrador no es visible para el público.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El evento no existe.")
    return a_salida(evento)


# ---------- Gestión (organizador y coordinación) ----------
@router.get("/api/gestion/eventos", response_model=list[EventoSalida])
def eventos_para_gestionar(usuario: Usuario = Depends(gestor), db: Session = Depends(obtener_db)):
    consulta = select(Evento)
    if usuario.rol == "ORGANIZADOR":
        consulta = consulta.where(Evento.organizador_id == usuario.id)
    eventos = db.scalars(consulta.order_by(Evento.fecha.desc(), Evento.hora_inicio)).all()
    return [a_salida(e) for e in eventos]


@router.post("/api/eventos", response_model=EventoSalida, status_code=status.HTTP_201_CREATED)
def crear_evento(
    datos: EventoEntrada,
    usuario: Usuario = Depends(requiere_rol("ORGANIZADOR")),
    db: Session = Depends(obtener_db),
):
    """El organizador crea el evento en estado BORRADOR."""
    if datos.fecha < date.today():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se puede crear un evento con fecha pasada.")
    evento = Evento(**datos.model_dump(), organizador_id=usuario.id, estado="BORRADOR")
    db.add(evento)
    db.commit()
    db.refresh(evento)
    return a_salida(evento)


@router.put("/api/eventos/{evento_id}", response_model=EventoSalida)
def modificar_evento(
    evento_id: int,
    datos: EventoEntrada,
    usuario: Usuario = Depends(gestor),
    db: Session = Depends(obtener_db),
):
    evento = buscar_evento(db, evento_id)
    verificar_permiso_gestion(usuario, evento)
    if evento.estado == "CANCELADO":
        raise HTTPException(status.HTTP_409_CONFLICT, "No se puede modificar un evento cancelado.")
    if datos.fecha != evento.fecha and datos.fecha < date.today():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se puede mover el evento a una fecha pasada.")
    if datos.cupo < evento.inscritos:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"El cupo no puede ser menor que las personas ya inscritas ({evento.inscritos}).",
        )
    for campo, valor in datos.model_dump().items():
        setattr(evento, campo, valor)
    db.commit()
    db.refresh(evento)
    return a_salida(evento)


@router.patch("/api/eventos/{evento_id}/publicar", response_model=EventoSalida)
def publicar_evento(evento_id: int, usuario: Usuario = Depends(gestor), db: Session = Depends(obtener_db)):
    """La publicación no requiere autorización adicional (decisión del cliente)."""
    evento = buscar_evento(db, evento_id)
    verificar_permiso_gestion(usuario, evento)
    if evento.estado != "BORRADOR":
        raise HTTPException(status.HTTP_409_CONFLICT, f"Solo se publica un evento en borrador (estado actual: {evento.estado}).")
    if evento.fecha < date.today():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se puede publicar un evento con fecha pasada.")
    evento.estado = "PUBLICADO"
    db.commit()
    return a_salida(evento)


@router.patch("/api/eventos/{evento_id}/cancelar", response_model=EventoSalida)
def cancelar_evento(evento_id: int, usuario: Usuario = Depends(gestor), db: Session = Depends(obtener_db)):
    evento = buscar_evento(db, evento_id)
    verificar_permiso_gestion(usuario, evento)
    if evento.estado == "CANCELADO":
        raise HTTPException(status.HTTP_409_CONFLICT, "El evento ya está cancelado.")
    evento.estado = "CANCELADO"
    db.commit()
    return a_salida(evento)
