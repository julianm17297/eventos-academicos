"""Configuración general de la aplicación.

Los valores se leen de variables de entorno (archivo .env). Si no existen,
se usan valores por defecto pensados para desarrollo local.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Cadena de conexión a la base de datos (SQLite por defecto: un archivo local).
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./eventos.db")

# Dominio de correo permitido: solo personas de la institución pueden registrarse.
DOMINIO_INSTITUCIONAL = os.getenv("DOMINIO_INSTITUCIONAL", "institucion.edu.co")

# Horas de vigencia de una sesión (token) después de iniciar sesión.
HORAS_SESION = int(os.getenv("HORAS_SESION", "8"))
