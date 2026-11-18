"""Servicios de inscripción: inscribirse, consultar mis inscripciones y cancelar.

Reglas de negocio aprobadas por la organización:
  RN-01 Solo personas de la institución con rol PARTICIPANTE pueden inscribirse.
  RN-02 Solo se puede inscribir en eventos PUBLICADOS.
  RN-03 No se aceptan inscripciones después de la fecha límite.
  RN-04 Si el cupo está agotado, la inscripción se rechaza (no hay lista de espera).
  RN-05 Una persona no puede inscribirse dos veces en el mismo evento.
  RN-06 Una persona no puede estar inscrita en dos actividades con horarios que se crucen.
  RN-07 El participante puede cancelar su inscripción antes de que empiece el evento;
        al cancelar, el cupo queda libre de nuevo.
"""
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import obtener_db
from ..models import Evento, Inscripcion, Usuario
from ..schemas import EventoResumen, InscripcionSalida
from ..security import requiere_rol
from .eventos import buscar_evento

router = APIRouter(tags=["Inscripciones"])

participante = requiere_rol("PARTICIPANTE")


def a_salida(inscripcion: Inscripcion) -> InscripcionSalida:
    return InscripcionSalida(
        id=inscripcion.id,
        estado=inscripcion.estado,
        creada_en=inscripcion.creada_en,
        cancelada_en=inscripcion.cancelada_en,
        evento=EventoResumen.model_validate(inscripcion.evento),
        asistencia=inscripcion.asistencia.estado if inscripcion.asistencia else None,
    )


def buscar_cruce_de_horario(db: Session, usuario: Usuario, evento: Evento) -> Evento | None:
    """Devuelve otro evento del participante que se cruce en fecha y hora (RN-06)."""
    consulta = (
        select(Evento)
        .join(Inscripcion, Inscripcion.evento_id == Evento.id)
        .where(
            Inscripcion.participante_id == usuario.id,
            Inscripcion.estado == "ACTIVA",
            Evento.id != evento.id,
            Evento.estado != "CANCELADO",
            Evento.fecha == evento.fecha,
            Evento.hora_inicio < evento.hora_fin,
            Evento.hora_fin > evento.hora_inicio,
        )
    )
    return db.scalars(consulta).first()


@router.post(
    "/api/eventos/{evento_id}/inscripciones",
    response_model=InscripcionSalida,
    status_code=status.HTTP_201_CREATED,
)
def inscribirse(evento_id: int, usuario: Usuario = Depends(participante), db: Session = Depends(obtener_db)):
    evento = buscar_evento(db, evento_id)
    if evento.estado == "BORRADOR":
        raise HTTPException(status.HTTP_404_NOT_FOUND, "El evento no existe.")
    if evento.estado == "CANCELADO":
        raise HTTPException(status.HTTP_409_CONFLICT, "El evento fue cancelado; no admite inscripciones.")
    if date.today() > evento.fecha_limite_inscripcion:
        raise HTTPException(status.HTTP_409_CONFLICT, "La fecha límite de inscripción ya pasó.")

    existente = db.scalar(
        select(Inscripcion).where(
            Inscripcion.evento_id == evento.id, Inscripcion.participante_id == usuario.id
        )
    )
    if existente and existente.estado == "ACTIVA":
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya está inscrito en este evento.")
    if evento.cupos_disponibles <= 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "El cupo del evento está agotado.")
    cruce = buscar_cruce_de_horario(db, usuario, evento)
    if cruce:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Ya está inscrito en «{cruce.titulo}» en un horario que se cruza con este evento.",
        )

    if existente:
        # Se había cancelado antes: se reactiva el mismo registro (no se duplica).
        existente.estado = "ACTIVA"
        existente.creada_en = datetime.now()
        existente.cancelada_en = None
        inscripcion = existente
    else:
        inscripcion = Inscripcion(evento_id=evento.id, participante_id=usuario.id, estado="ACTIVA")
        db.add(inscripcion)
    db.commit()
    db.refresh(inscripcion)
    return a_salida(inscripcion)


@router.get("/api/inscripciones/mias", response_model=list[InscripcionSalida])
def mis_inscripciones(usuario: Usuario = Depends(participante), db: Session = Depends(obtener_db)):
    inscripciones = db.scalars(
        select(Inscripcion)
        .join(Evento)
        .where(Inscripcion.participante_id == usuario.id)
        .order_by(Evento.fecha.desc())
    ).all()
    return [a_salida(i) for i in inscripciones]


@router.patch("/api/inscripciones/{inscripcion_id}/cancelar", response_model=InscripcionSalida)
def cancelar_inscripcion(
    inscripcion_id: int, usuario: Usuario = Depends(participante), db: Session = Depends(obtener_db)
):
    inscripcion = db.get(Inscripcion, inscripcion_id)
    if inscripcion is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La inscripción no existe.")
    if inscripcion.participante_id != usuario.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo puede cancelar sus propias inscripciones.")
    if inscripcion.estado == "CANCELADA":
        raise HTTPException(status.HTTP_409_CONFLICT, "La inscripción ya estaba cancelada.")
    evento = inscripcion.evento
    if datetime.now() >= datetime.combine(evento.fecha, evento.hora_inicio):
        raise HTTPException(status.HTTP_409_CONFLICT, "No se puede cancelar: el evento ya comenzó o terminó.")
    inscripcion.estado = "CANCELADA"
    inscripcion.cancelada_en = datetime.now()
    db.commit()
    return a_salida(inscripcion)
