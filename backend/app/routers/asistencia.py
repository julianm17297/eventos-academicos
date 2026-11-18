"""Servicios de asistencia: lista de participantes y registro/corrección de asistencia.

Reglas de negocio aprobadas por la organización:
  RN-08 La asistencia se registra el día del evento, por cada actividad.
  RN-09 Los estados de asistencia son ASISTIO o NO_ASISTIO.
  RN-10 Un registro de asistencia puede corregirse.
  RN-11 No se registra asistencia a personas que no estén inscritas (inscripción ACTIVA).
"""
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..database import obtener_db
from ..models import Asistencia, Inscripcion, Usuario
from ..schemas import AsistenciaEntrada, ListaParticipantesSalida, ParticipanteEnLista
from ..security import requiere_rol
from .eventos import a_salida, buscar_evento, verificar_permiso_gestion

router = APIRouter(tags=["Asistencia"])

gestor = requiere_rol("ORGANIZADOR", "COORDINACION")


def fila_participante(inscripcion: Inscripcion) -> ParticipanteEnLista:
    asistencia = inscripcion.asistencia
    return ParticipanteEnLista(
        inscripcion_id=inscripcion.id,
        participante_id=inscripcion.participante.id,
        documento=inscripcion.participante.documento,
        nombre=inscripcion.participante.nombre,
        correo=inscripcion.participante.correo,
        estado_inscripcion=inscripcion.estado,
        asistencia=asistencia.estado if asistencia else None,
        asistencia_registrada_en=(asistencia.actualizada_en or asistencia.registrada_en) if asistencia else None,
    )


@router.get("/api/eventos/{evento_id}/participantes", response_model=ListaParticipantesSalida)
def lista_participantes(evento_id: int, usuario: Usuario = Depends(gestor), db: Session = Depends(obtener_db)):
    evento = buscar_evento(db, evento_id)
    verificar_permiso_gestion(usuario, evento)
    inscripciones = sorted(evento.inscripciones, key=lambda i: (i.estado != "ACTIVA", i.participante.nombre))
    return ListaParticipantesSalida(
        evento=a_salida(evento),
        participantes=[fila_participante(i) for i in inscripciones],
    )


@router.put("/api/eventos/{evento_id}/asistencia/{inscripcion_id}", response_model=ParticipanteEnLista)
def registrar_asistencia(
    evento_id: int,
    inscripcion_id: int,
    datos: AsistenciaEntrada,
    response: Response,
    usuario: Usuario = Depends(gestor),
    db: Session = Depends(obtener_db),
):
    evento = buscar_evento(db, evento_id)
    verificar_permiso_gestion(usuario, evento)
    if evento.estado != "PUBLICADO":
        raise HTTPException(status.HTTP_409_CONFLICT, "Solo se registra asistencia en eventos publicados.")

    inscripcion = db.get(Inscripcion, inscripcion_id)
    if inscripcion is None or inscripcion.evento_id != evento.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La persona no tiene inscripción en este evento.")
    if inscripcion.estado != "ACTIVA":
        raise HTTPException(status.HTTP_409_CONFLICT, "No se registra asistencia de una inscripción cancelada.")

    hoy = date.today()
    if inscripcion.asistencia is None:
        if hoy != evento.fecha:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"La asistencia se registra el día del evento ({evento.fecha.isoformat()}).",
            )
        inscripcion.asistencia = Asistencia(estado=datos.estado, registrada_por_id=usuario.id)
        response.status_code = status.HTTP_201_CREATED
    else:
        # Corrección de un registro existente (RN-10).
        inscripcion.asistencia.estado = datos.estado
        inscripcion.asistencia.registrada_por_id = usuario.id
        inscripcion.asistencia.actualizada_en = datetime.now()
    db.commit()
    db.refresh(inscripcion)
    return fila_participante(inscripcion)
