from typing import Optional
from app.domain.carrera import Carrera
from app.domain.repositorio_carrera import RepositorioCarrera


class CasoUsoConsultarCarreras:
    """Caso de uso para consultar y filtrar información de carreras universitarias."""

    def __init__(self, repositorio: RepositorioCarrera) -> None:
        self.repositorio = repositorio

    def obtener_por_id(self, id_carrera: str) -> Optional[Carrera]:
        """Obtiene el detalle de una carrera por su identificador único."""
        if not id_carrera or not id_carrera.strip():
            return None
        return self.repositorio.obtener_por_id(id_carrera.strip())

    def listar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        limite: int = 100,
        desplazamiento: int = 0,
    ) -> list[Carrera]:
        """Lista carreras aplicando filtros opcionales y paginación."""
        return self.repositorio.listar(
            institucion=institucion,
            area_formacion=area_formacion,
            modalidad=modalidad,
            limite=limite,
            desplazamiento=desplazamiento,
        )

    def contar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
    ) -> int:
        """Cuenta el total de carreras que cumplen con los filtros."""
        return self.repositorio.contar(
            institucion=institucion,
            area_formacion=area_formacion,
            modalidad=modalidad,
        )
