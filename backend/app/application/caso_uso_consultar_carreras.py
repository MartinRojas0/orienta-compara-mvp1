from typing import Optional
from app.domain.carrera import Carrera
from app.domain.repositorio_carrera import RepositorioCarrera


class CasoUsoConsultarCarreras:
    """Caso de uso para consultar y filtrar información de carreras universitarias."""

    def __init__(self, repositorio: RepositorioCarrera) -> None:
        self.repositorio = repositorio

    @staticmethod
    def normalizar_id(id_carrera: str) -> str:
        """Normaliza variantes del identificador (ej: '2', '02', 'c02', 'C02' -> 'C02')."""
        limpio = id_carrera.strip()
        if limpio.isdigit():
            return f"C{int(limpio):02d}"
        if limpio.upper().startswith("C") and limpio[1:].isdigit():
            return f"C{int(limpio[1:]):02d}"
        return limpio.upper()

    def obtener_por_id(self, id_carrera: str) -> Optional[Carrera]:
        """Obtiene el detalle de una carrera por su identificador único."""
        if not id_carrera or not id_carrera.strip():
            return None

        # Intentar con ID normalizado
        id_norm = self.normalizar_id(id_carrera)
        carrera = self.repositorio.obtener_por_id(id_norm)
        if carrera:
            return carrera

        # Si no se encuentra, intentar con el ID exacto original
        if id_norm != id_carrera.strip():
            return self.repositorio.obtener_por_id(id_carrera.strip())

        return None

    def listar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        ubicacion: Optional[str] = None,
        limite: int = 100,
        desplazamiento: int = 0,
    ) -> list[Carrera]:
        """Lista carreras aplicando filtros opcionales y paginación."""
        return self.repositorio.listar(
            institucion=institucion,
            area_formacion=area_formacion,
            modalidad=modalidad,
            ubicacion=ubicacion,
            limite=limite,
            desplazamiento=desplazamiento,
        )

    def contar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        ubicacion: Optional[str] = None,
    ) -> int:
        """Cuenta el total de carreras que cumplen con los filtros."""
        return self.repositorio.contar(
            institucion=institucion,
            area_formacion=area_formacion,
            modalidad=modalidad,
            ubicacion=ubicacion,
        )
