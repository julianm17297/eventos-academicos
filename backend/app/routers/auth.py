"""Servicios de autenticación: registro de participantes, inicio y cierre de sesión."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import obtener_db
from ..models import Sesion, Usuario
from ..schemas import LoginEntrada, LoginSalida, RegistroEntrada, UsuarioSalida
from ..security import (
    cifrar_clave,
    crear_sesion,
    obtener_sesion_actual,
    obtener_usuario_actual,
    verificar_clave,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioSalida, status_code=status.HTTP_201_CREATED)
def registrar_participante(datos: RegistroEntrada, db: Session = Depends(obtener_db)):
    """Registro de una persona de la institución (siempre con rol PARTICIPANTE)."""
    existente = db.scalar(
        select(Usuario).where(or_(Usuario.correo == datos.correo, Usuario.documento == datos.documento))
    )
    if existente:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ya existe una cuenta con ese correo o documento.")
    usuario = Usuario(
        documento=datos.documento,
        nombre=datos.nombre,
        correo=datos.correo,
        clave_hash=cifrar_clave(datos.clave),
        rol="PARTICIPANTE",
    )
    db.add(usuario)
    db.commit()
    return usuario


@router.post("/login", response_model=LoginSalida)
def iniciar_sesion(datos: LoginEntrada, db: Session = Depends(obtener_db)):
    usuario = db.scalar(select(Usuario).where(Usuario.correo == datos.correo.strip().lower()))
    # Mensaje genérico: no revela si el correo existe o no.
    if usuario is None or not verificar_clave(datos.clave, usuario.clave_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Correo o contraseña incorrectos.")
    sesion = crear_sesion(db, usuario)
    return LoginSalida(token=sesion.token, expira_en=sesion.expira_en, usuario=usuario)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def cerrar_sesion(sesion: Sesion = Depends(obtener_sesion_actual), db: Session = Depends(obtener_db)):
    db.delete(db.merge(sesion))
    db.commit()


@router.get("/yo", response_model=UsuarioSalida)
def usuario_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario
