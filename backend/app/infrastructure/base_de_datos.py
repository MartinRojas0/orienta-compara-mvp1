import os
from typing import Generator, Optional
from dotenv import load_dotenv
from sqlmodel import Session, SQLModel, create_engine

# Carga variables de entorno desde .env si existe
load_dotenv()

DATABASE_URL_DEFAULT = os.getenv("DATABASE_URL", "sqlite:///./orienta.db")


def crear_motor(url_db: Optional[str] = None):
    """Crea y devuelve un motor de base de datos SQLModel/SQLAlchemy."""
    url = url_db or DATABASE_URL_DEFAULT
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(url, echo=False, connect_args=connect_args)


motor = crear_motor()


def crear_tablas(engine=None) -> None:
    """Crea todas las tablas registradas en SQLModel si aún no existen."""
    motor_actual = engine or motor
    SQLModel.metadata.create_all(motor_actual)


def obtener_sesion(engine=None) -> Generator[Session, None, None]:
    """Generador de sesiones para ser utilizado como contexto o dependencia."""
    motor_actual = engine or motor
    with Session(motor_actual) as sesion:
        yield sesion
