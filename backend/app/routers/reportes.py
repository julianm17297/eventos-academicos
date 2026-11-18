"""Servicios de información consolidada para la coordinación.

La coordinación necesita el porcentaje de asistencia por actividad y por periodos.
Porcentaje de asistencia = personas que asistieron / personas inscritas (activas) x 100.
"""
from collections import defaultdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import obtener_db
from ..models import Evento, Usuario
from ..schemas import ReporteEvento, ReportePeriodo
from ..security import requiere_rol

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

coordinacion = requiere_rol("COORDINACION")


def porcentaje(parte: int, total: int) -> float:
    return round(parte * 100 / total, 1) if total else 0.0


def eventos_en_rango(db: Session, desde: date | None, hasta: date | None) -> list[Evento]:
    if desde and hasta and desde > hasta:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "La fecha 'desde' no puede ser posterior a 'hasta'.")
    consulta = select(Evento).where(Evento.estado != "BORRADOR")
    if desde:
        consulta = consulta.where(Evento.fecha >= desde)
    if hasta:
        consulta = consulta.where(Evento.fecha <= hasta)
    return list(db.scalars(consulta.order_by(Evento.fecha, Evento.hora_inicio)).all())


def resumen_evento(evento: Evento) -> ReporteEvento:
    activas = [i for i in evento.inscripciones if i.estado == "ACTIVA"]
    asistieron = sum(1 for i in activas if i.asistencia and i.asistencia.estado == "ASISTIO")
    no_asistieron = sum(1 for i in activas if i.asistencia and i.asistencia.estado == "NO_ASISTIO")
    return ReporteEvento(
        evento_id=evento.id,
        titulo=evento.titulo,
        tipo=evento.tipo,
        fecha=evento.fecha,
        estado=evento.estado,
        organizador=evento.organizador.nombre,
        cupo=evento.cupo,
        inscritos=len(activas),
        cupos_disponibles=evento.cupos_disponibles,
        asistieron=asistieron,
        no_asistieron=no_asistieron,
        sin_registro=len(activas) - asistieron - no_asistieron,
        porcentaje_asistencia=porcentaje(asistieron, len(activas)),
    )


@router.get("/eventos", response_model=list[ReporteEvento])
def reporte_por_actividad(
    desde: date | None = None,
    hasta: date | None = None,
    _usuario: Usuario = Depends(coordinacion),
    db: Session = Depends(obtener_db),
):
    return [resumen_evento(e) for e in eventos_en_rango(db, desde, hasta)]


@router.get("/periodos", response_model=list[ReportePeriodo])
def reporte_por_periodo(
    desde: date | None = None,
    hasta: date | None = None,
    _usuario: Usuario = Depends(coordinacion),
    db: Session = Depends(obtener_db),
):
    """Agrupa por mes (AAAA-MM) los eventos ya realizados (fecha de hoy o anterior).

    Los eventos cancelados y los que aún no ocurren no cuentan, porque todavía
    no tienen asistencia y bajarían el porcentaje de forma engañosa.
    """
    grupos: dict[str, list[ReporteEvento]] = defaultdict(list)
    for evento in eventos_en_rango(db, desde, hasta):
        if evento.estado == "CANCELADO" or evento.fecha > date.today():
            continue
        grupos[evento.fecha.strftime("%Y-%m")].append(resumen_evento(evento))
    resultado = []
    for periodo in sorted(grupos):
        filas = grupos[periodo]
        inscritos = sum(f.inscritos for f in filas)
        asistieron = sum(f.asistieron for f in filas)
        resultado.append(
            ReportePeriodo(
                periodo=periodo,
                eventos=len(filas),
                cupo_total=sum(f.cupo for f in filas),
                inscritos=inscritos,
                asistieron=asistieron,
                porcentaje_asistencia=porcentaje(asistieron, inscritos),
            )
        )
    return resultado
