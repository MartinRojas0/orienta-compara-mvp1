from pathlib import Path
from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from app.adapters.lector_carreras_excel import LectorCarrerasExcel
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite
from app.application.caso_uso_consultar_carreras import CasoUsoConsultarCarreras
from app.application.caso_uso_importar_carreras import CasoUsoImportarCarreras
from app.infrastructure.base_de_datos import obtener_sesion
from app.main import app


@pytest.fixture(name="ruta_excel_real")
def fixture_ruta_excel_real() -> Path:
    """Retorna la ruta al archivo Excel real de datos ampliados."""
    ruta_raiz = Path(__file__).resolve().parent.parent.parent / "data" / "ORIENTA_Lima_Norte_Ampliado.xlsx"
    if not ruta_raiz.exists():
        ruta_directa = Path("data/ORIENTA_Lima_Norte_Ampliado.xlsx")
        if ruta_directa.exists():
            return ruta_directa.resolve()
    return ruta_raiz.resolve()


@pytest.fixture(name="motor_prueba")
def fixture_motor_prueba():
    """Crea un motor SQLite en memoria aislado para pruebas."""
    motor = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(motor)
    return motor


@pytest.fixture(name="sesion_prueba")
def fixture_sesion_prueba(motor_prueba) -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos para cada prueba."""
    with Session(motor_prueba) as sesion:
        yield sesion


@pytest.fixture(name="repositorio_prueba")
def fixture_repositorio_prueba(sesion_prueba) -> RepositorioCarreraSQLite:
    """Proporciona una instancia del repositorio SQLite."""
    return RepositorioCarreraSQLite(sesion_prueba)


@pytest.fixture(name="lector_excel")
def fixture_lector_excel() -> LectorCarrerasExcel:
    return LectorCarrerasExcel()


@pytest.fixture(name="caso_uso_importar")
def fixture_caso_uso_importar(repositorio_prueba, lector_excel) -> CasoUsoImportarCarreras:
    return CasoUsoImportarCarreras(repositorio=repositorio_prueba, lector=lector_excel)


@pytest.fixture(name="caso_uso_consultar")
def fixture_caso_uso_consultar(repositorio_prueba) -> CasoUsoConsultarCarreras:
    return CasoUsoConsultarCarreras(repositorio=repositorio_prueba)


@pytest.fixture(name="cliente_api")
def fixture_cliente_api(sesion_prueba) -> Generator[TestClient, None, None]:
    """Proporciona un cliente de prueba para la API FastAPI con sesión sobreescrita."""

    def sobreescribir_sesion():
        yield sesion_prueba

    app.dependency_overrides[obtener_sesion] = sobreescribir_sesion
    with TestClient(app) as cliente:
        yield cliente
    app.dependency_overrides.clear()
