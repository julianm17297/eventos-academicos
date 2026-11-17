"""Datos de ejemplo FICTICIOS para pruebas y demostración.

Uso:
    python -m app.seed      -> borra la base de datos y la vuelve a crear con estos datos.

Las fechas se calculan a partir del día de hoy, para que la demostración funcione
cualquier día (hay un evento hoy para registrar asistencia, eventos futuros
para inscribirse y eventos pasados para los reportes por periodo).

Todas las cuentas usan la contraseña de prueba: Clave123*
"""
from datetime import date, time, timedelta

from sqlalchemy import select

from .database import Base, SesionLocal, engine
from .models import Asistencia, Evento, Inscripcion, Usuario
from .security import cifrar_clave

CLAVE_DEMO = "Clave123*"
DOMINIO = "institucion.edu.co"

USUARIOS = [
    # (documento, nombre, usuario del correo, rol)
    ("1000000001", "Laura Gómez", "coordinacion", "COORDINACION"),
    ("1000000002", "Carlos Ruiz", "organizador1", "ORGANIZADOR"),
    ("1000000003", "Marta Díaz", "organizador2", "ORGANIZADOR"),
    ("2000000001", "Ana Torres", "estudiante1", "PARTICIPANTE"),
    ("2000000002", "Bruno Castro", "estudiante2", "PARTICIPANTE"),
    ("2000000003", "Camila Rojas", "estudiante3", "PARTICIPANTE"),
    ("2000000004", "Daniel Pérez", "estudiante4", "PARTICIPANTE"),
    ("2000000005", "Elena Vargas", "estudiante5", "PARTICIPANTE"),
    ("3000000001", "Felipe Moreno", "docente1", "PARTICIPANTE"),
]


def cargar_datos(db) -> None:
    hoy = date.today()
    clave = cifrar_clave(CLAVE_DEMO)
    u = {}
    for documento, nombre, usuario, rol in USUARIOS:
        u[usuario] = Usuario(
            documento=documento, nombre=nombre, correo=f"{usuario}@{DOMINIO}", clave_hash=clave, rol=rol
        )
        db.add(u[usuario])
    db.flush()

    def evento(titulo, tipo, dias, inicio, fin, cupo, organizador, estado="PUBLICADO", limite=None, lugar="Auditorio principal"):
        e = Evento(
            titulo=titulo,
            descripcion=f"{titulo}. Actividad académica abierta a la comunidad institucional.",
            tipo=tipo,
            lugar=lugar,
            fecha=hoy + timedelta(days=dias),
            hora_inicio=time(*inicio),
            hora_fin=time(*fin),
            cupo=cupo,
            fecha_limite_inscripcion=hoy + timedelta(days=dias if limite is None else limite),
            estado=estado,
            organizador_id=u[organizador].id,
        )
        db.add(e)
        db.flush()
        return e

    def inscribir(e, *usuarios):
        lista = []
        for nombre in usuarios:
            i = Inscripcion(evento_id=e.id, participante_id=u[nombre].id, estado="ACTIVA")
            db.add(i)
            lista.append(i)
        db.flush()
        return lista

    def asistencia(inscripciones, estados, registrador):
        for i, estado in zip(inscripciones, estados):
            db.add(Asistencia(inscripcion_id=i.id, estado=estado, registrada_por_id=u[registrador].id))

    # --- Eventos de hoy y futuros (demostración) ---
    e1 = evento("Conferencia: Inteligencia artificial en la educación", "CONFERENCIA", 0, (7, 0), (9, 0), 30, "organizador1")
    inscribir(e1, "estudiante1", "estudiante2", "estudiante3", "docente1")

    e2 = evento("Taller de Git y GitHub", "TALLER", 3, (14, 0), (17, 0), 3, "organizador1", lugar="Sala de cómputo 2")
    inscribir(e2, "estudiante1", "estudiante2")

    evento("Seminario de bases de datos", "SEMINARIO", 3, (15, 0), (16, 0), 20, "organizador2", lugar="Salón 204")

    evento("Capacitación en primeros auxilios", "CAPACITACION", 10, (8, 0), (12, 0), 25, "organizador2", limite=-1, lugar="Gimnasio")

    e6 = evento("Conferencia de emprendimiento", "CONFERENCIA", 7, (10, 0), (12, 0), 40, "organizador2")
    inscribir(e6, "estudiante4", "estudiante5")

    evento("Seminario de investigación formativa", "SEMINARIO", 15, (9, 0), (11, 0), 35, "organizador1", estado="BORRADOR", lugar="Salón 101")

    # --- Eventos pasados (para reportes por actividad y por periodo) ---
    p1 = evento("Taller de Python básico", "TALLER", -40, (14, 0), (17, 0), 20, "organizador1", limite=-41, lugar="Sala de cómputo 1")
    asistencia(inscribir(p1, "estudiante1", "estudiante2", "estudiante3", "estudiante4", "estudiante5"),
               ["ASISTIO", "ASISTIO", "ASISTIO", "ASISTIO", "NO_ASISTIO"], "organizador1")

    p2 = evento("Conferencia de ciberseguridad", "CONFERENCIA", -35, (9, 0), (11, 0), 50, "organizador2", limite=-36)
    asistencia(inscribir(p2, "estudiante1", "estudiante2", "estudiante3", "estudiante4", "estudiante5", "docente1"),
               ["ASISTIO", "NO_ASISTIO", "ASISTIO", "NO_ASISTIO", "ASISTIO", "ASISTIO"], "organizador2")

    evento("Taller de fotografía digital", "TALLER", -20, (14, 0), (16, 0), 15, "organizador2", estado="CANCELADO", limite=-21)

    p4 = evento("Seminario de metodologías ágiles", "SEMINARIO", -12, (8, 0), (10, 0), 15, "organizador1", limite=-13, lugar="Salón 204")
    asistencia(inscribir(p4, "estudiante2", "estudiante3", "estudiante5", "docente1"),
               ["ASISTIO", "ASISTIO", "NO_ASISTIO", "ASISTIO"], "organizador1")

    db.commit()


def cargar_si_esta_vacia() -> None:
    with SesionLocal() as db:
        if db.scalar(select(Usuario).limit(1)) is None:
            cargar_datos(db)


def reiniciar() -> None:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SesionLocal() as db:
        cargar_datos(db)
    print("Base de datos reiniciada con datos de ejemplo. Contraseña de todas las cuentas:", CLAVE_DEMO)


if __name__ == "__main__":
    reiniciar()
