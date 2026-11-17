"""Esquemas de entrada y salida de la API (validación de datos)."""
import re
from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from .config import DOMINIO_INSTITUCIONAL

Rol = Literal["PARTICIPANTE", "ORGANIZADOR", "COORDINACION"]
TipoEvento = Literal["CONFERENCIA", "TALLER", "SEMINARIO", "CAPACITACION"]
EstadoAsistencia = Literal["ASISTIO", "NO_ASISTIO"]

PATRON_CORREO = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


# ---------- Autenticación ----------
class RegistroEntrada(BaseModel):
    documento: str = Field(min_length=5, max_length=20, pattern=r"^\d+$")
    nombre: str = Field(min_length=3, max_length=120)
    correo: str = Field(max_length=120)
    clave: str = Field(min_length=8, max_length=64)

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres.")
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo_institucional(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if not PATRON_CORREO.match(valor):
            raise ValueError("El correo no tiene un formato válido.")
        if not valor.endswith("@" + DOMINIO_INSTITUCIONAL):
            raise ValueError(f"Solo se permiten correos institucionales (@{DOMINIO_INSTITUCIONAL}).")
        return valor


class LoginEntrada(BaseModel):
    correo: str
    clave: str


class UsuarioSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    documento: str
    nombre: str
    correo: str
    rol: Rol


class LoginSalida(BaseModel):
    token: str
    expira_en: datetime
    usuario: UsuarioSalida


# ---------- Eventos ----------
class EventoEntrada(BaseModel):
    titulo: str = Field(min_length=3, max_length=150)
    descripcion: str = Field(default="", max_length=2000)
    tipo: TipoEvento
    lugar: str = Field(min_length=2, max_length=120)
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupo: int = Field(gt=0, le=1000)
    fecha_limite_inscripcion: date

    @field_validator("titulo", "lugar")
    @classmethod
    def sin_espacios_vacios(cls, valor: str) -> str:
        valor = valor.strip()
        if len(valor) < 2:
            raise ValueError("El campo no puede estar vacío.")
        return valor

    @model_validator(mode="after")
    def validar_fechas_y_horas(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio.")
        if self.fecha_limite_inscripcion > self.fecha:
            raise ValueError("La fecha límite de inscripción no puede ser posterior a la fecha del evento.")
        return self


class OrganizadorResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str


class EventoSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    descripcion: str
    tipo: TipoEvento
    lugar: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    cupo: int
    fecha_limite_inscripcion: date
    estado: str
    inscritos: int
    cupos_disponibles: int
    inscripciones_abiertas: bool = False
    organizador: OrganizadorResumen


# ---------- Inscripciones ----------
class EventoResumen(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    titulo: str
    tipo: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    lugar: str
    estado: str


class InscripcionSalida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    estado: str
    creada_en: datetime
    cancelada_en: datetime | None
    evento: EventoResumen
    asistencia: str | None = None


# ---------- Asistencia ----------
class AsistenciaEntrada(BaseModel):
    estado: EstadoAsistencia


class ParticipanteEnLista(BaseModel):
    inscripcion_id: int
    participante_id: int
    documento: str
    nombre: str
    correo: str
    estado_inscripcion: str
    asistencia: str | None
    asistencia_registrada_en: datetime | None


class ListaParticipantesSalida(BaseModel):
    evento: EventoSalida
    participantes: list[ParticipanteEnLista]


# ---------- Reportes ----------
class ReporteEvento(BaseModel):
    evento_id: int
    titulo: str
    tipo: str
    fecha: date
    estado: str
    organizador: str
    cupo: int
    inscritos: int
    cupos_disponibles: int
    asistieron: int
    no_asistieron: int
    sin_registro: int
    porcentaje_asistencia: float


class ReportePeriodo(BaseModel):
    periodo: str
    eventos: int
    cupo_total: int
    inscritos: int
    asistieron: int
    porcentaje_asistencia: float
