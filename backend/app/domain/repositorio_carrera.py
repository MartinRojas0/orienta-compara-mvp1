from abc import ABC, abstractmethod
from typing import Optional
from app.domain.carrera import Carrera


class RepositorioCarrera(ABC):
    """Contrato de persistencia para la entidad Carrera."""

    @abstractmethod
    def guardar(self, carrera: Carrera) -> Carrera:
        """Guarda o actualiza una carrera individual."""
        pass

    @abstractmethod
    def guardar_muchas(self, carreras: list[Carrera]) -> tuple[int, int]:
        """Guarda o actualiza una lista de carreras en una sola transacción.

        Retorna una tupla con (insertados, actualizados).
        """
        pass

    @abstractmethod
    def obtener_por_id(self, id_carrera: str) -> Optional[Carrera]:
        """Obtiene una carrera por su identificador único."""
        pass

    @abstractmethod
    def listar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        ubicacion: Optional[str] = None,
        limite: int = 100,
        desplazamiento: int = 0,
    ) -> list[Carrera]:
        """Lista carreras aplicando filtros opcionales."""
        pass

    @abstractmethod
    def contar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        ubicacion: Optional[str] = None,
    ) -> int:
        """Cuenta el total de carreras según filtros opcionales."""
        pass

    @abstractmethod
    def existe_por_id(self, id_carrera: str) -> bool:
        """Comprueba si ya existe una carrera con el id especificado."""
        pass
