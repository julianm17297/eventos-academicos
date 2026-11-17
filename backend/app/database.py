"""Conexión a la base de datos relacional mediante SQLAlchemy."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

es_sqlite = DATABASE_URL.startswith("sqlite")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if es_sqlite else {},
)

if es_sqlite:
    # SQLite no aplica llaves foráneas a menos que se active explícitamente.
    @event.listens_for(engine, "connect")
    def _activar_llaves_foraneas(conexion, _registro):
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SesionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Clase base de todas las tablas."""


def obtener_db():
    """Entrega una sesión de base de datos por solicitud y la cierra al final."""
    db = SesionLocal()
    try:
        yield db
    finally:
        db.close()
