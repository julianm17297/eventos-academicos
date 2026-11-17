"""Modelo de datos (tablas de la base de datos).

Entidades: Usuario, Sesion, Evento, Inscripcion, Asistencia.
"""
from datetime import date, datetime, time

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base

# Valores permitidos (se validan también en los esquemas de la API).
ROLES = ("PARTICIPANTE", "ORGANIZADOR", "COORDINACION")
TIPOS_EVENTO = ("CONFERENCIA", "TALLER", "SEMINARIO", "CAPACITACION")
ESTADOS_EVENTO = ("BORRADOR", "PUBLICADO", "CANCELADO")
ESTADOS_INSCRIPCION = ("ACTIVA", "CANCELADA")
ESTADOS_ASISTENCIA = ("ASISTIO", "NO_ASISTIO")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    documento: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120))
    correo: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    clave_hash: Mapped[str] = mapped_column(String(200))
    rol: Mapped[str] = mapped_column(String(20), default="PARTICIPANTE")
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    __table_args__ = (
        CheckConstraint(f"rol IN {ROLES}", name="ck_usuario_rol"),
    )


class Sesion(Base):
    """Token entregado al iniciar sesión. Se elimina al cerrar sesión."""

    __tablename__ = "sesiones"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"))
    expira_en: Mapped[datetime] = mapped_column(DateTime)

    usuario: Mapped[Usuario] = relationship()


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str] = mapped_column(Text, default="")
    tipo: Mapped[str] = mapped_column(String(20))
    lugar: Mapped[str] = mapped_column(String(120))
    fecha: Mapped[date] = mapped_column(Date)
    hora_inicio: Mapped[time] = mapped_column(Time)
    hora_fin: Mapped[time] = mapped_column(Time)
    cupo: Mapped[int] = mapped_column(Integer)
    fecha_limite_inscripcion: Mapped[date] = mapped_column(Date)
    estado: Mapped[str] = mapped_column(String(20), default="BORRADOR")
    organizador_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    organizador: Mapped[Usuario] = relationship()
    inscripciones: Mapped[list["Inscripcion"]] = relationship(back_populates="evento")

    __table_args__ = (
        CheckConstraint("cupo > 0", name="ck_evento_cupo_positivo"),
        CheckConstraint("hora_fin > hora_inicio", name="ck_evento_horario"),
        CheckConstraint(f"estado IN {ESTADOS_EVENTO}", name="ck_evento_estado"),
        CheckConstraint(f"tipo IN {TIPOS_EVENTO}", name="ck_evento_tipo"),
    )

    @property
    def inscritos(self) -> int:
        return sum(1 for i in self.inscripciones if i.estado == "ACTIVA")

    @property
    def cupos_disponibles(self) -> int:
        return max(self.cupo - self.inscritos, 0)


class Inscripcion(Base):
    __tablename__ = "inscripciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    evento_id: Mapped[int] = mapped_column(ForeignKey("eventos.id"))
    participante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    estado: Mapped[str] = mapped_column(String(20), default="ACTIVA")
    creada_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    cancelada_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    evento: Mapped[Evento] = relationship(back_populates="inscripciones")
    participante: Mapped[Usuario] = relationship()
    asistencia: Mapped["Asistencia | None"] = relationship(
        back_populates="inscripcion", uselist=False
    )

    __table_args__ = (
        # Una persona tiene como máximo un registro por evento (evita duplicados).
        UniqueConstraint("evento_id", "participante_id", name="uq_inscripcion_evento_participante"),
        CheckConstraint(f"estado IN {ESTADOS_INSCRIPCION}", name="ck_inscripcion_estado"),
    )


class Asistencia(Base):
    __tablename__ = "asistencias"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inscripcion_id: Mapped[int] = mapped_column(ForeignKey("inscripciones.id"), unique=True)
    estado: Mapped[str] = mapped_column(String(20))
    registrada_por_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    registrada_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    actualizada_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    inscripcion: Mapped[Inscripcion] = relationship(back_populates="asistencia")
    registrada_por: Mapped[Usuario] = relationship()

    __table_args__ = (
        CheckConstraint(f"estado IN {ESTADOS_ASISTENCIA}", name="ck_asistencia_estado"),
    )
