"""Funciones de seguridad: cifrado de contraseñas, sesiones y control de roles."""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import HORAS_SESION
from .database import obtener_db
from .models import Sesion, Usuario

ITERACIONES = 200_000


def cifrar_clave(clave: str) -> str:
    """Guarda la contraseña cifrada (nunca en texto plano)."""
    sal = secrets.token_hex(16)
    resumen = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal.encode(), ITERACIONES)
    return f"{sal}${resumen.hex()}"


def verificar_clave(clave: str, clave_hash: str) -> bool:
    sal, resumen = clave_hash.split("$", 1)
    calculado = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal.encode(), ITERACIONES)
    return hmac.compare_digest(calculado.hex(), resumen)


def crear_sesion(db: Session, usuario: Usuario) -> Sesion:
    sesion = Sesion(
        token=secrets.token_hex(32),
        usuario_id=usuario.id,
        expira_en=datetime.now() + timedelta(hours=HORAS_SESION),
    )
    db.add(sesion)
    db.commit()
    return sesion


esquema_bearer = HTTPBearer(auto_error=False)


def obtener_sesion_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    db: Session = Depends(obtener_db),
) -> Sesion:
    """Valida el token enviado en el encabezado Authorization: Bearer <token>."""
    if credenciales is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Debe iniciar sesión.")
    sesion = db.get(Sesion, credenciales.credentials)
    if sesion is None or sesion.expira_en < datetime.now():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sesión inválida o vencida. Inicie sesión de nuevo.")
    return sesion


def obtener_usuario_actual(sesion: Sesion = Depends(obtener_sesion_actual)) -> Usuario:
    return sesion.usuario


def requiere_rol(*roles: str):
    """Permite el acceso solo a los usuarios con alguno de los roles indicados."""

    def verificar(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
        if usuario.rol not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "No tiene permiso para realizar esta acción.")
        return usuario

    return verificar
