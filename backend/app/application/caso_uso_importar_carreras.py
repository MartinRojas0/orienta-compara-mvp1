from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol
from app.domain.carrera import Carrera
from app.domain.repositorio_carrera import RepositorioCarrera


class PuertoLectorCarreras(Protocol):
    """Protocolo / Puerto para lectores de carreras desde fuentes externas."""

    def leer(self, ruta_archivo: str | Path, nombre_hoja: Optional[str] = None) -> list[Carrera]:
        ...


@dataclass
class ResultadoImportacion:
    """Información consolidada del proceso de importación de carreras."""

    total_leidos: int
    total_insertados: int
    total_actualizados: int
    ruta_archivo: str
    mensaje: str

    @property
    def exitoso(self) -> bool:
        return self.total_leidos > 0 and (self.total_insertados + self.total_actualizados) == self.total_leidos


class ErrorImportacionCarreras(Exception):
    """Excepción de negocio ante fallas durante la importación de carreras."""

    pass


class CasoUsoImportarCarreras:
    """Caso de uso para importar y sincronizar carreras desde una fuente de datos (Excel)."""

    def __init__(
        self,
        repositorio: RepositorioCarrera,
        lector: Optional[PuertoLectorCarreras] = None,
    ) -> None:
        self.repositorio = repositorio
        if lector is None:
            from app.adapters.lector_carreras_excel import LectorCarrerasExcel

            self.lector: PuertoLectorCarreras = LectorCarrerasExcel()
        else:
            self.lector = lector

    def ejecutar(
        self,
        ruta_archivo: str | Path,
        nombre_hoja: Optional[str] = None,
    ) -> ResultadoImportacion:
        """Ejecuta la lectura del archivo y la persistencia transaccional e idempotente en la base de datos.

        Args:
            ruta_archivo: Ubicación del archivo de datos.
            nombre_hoja: Nombre opcional de la hoja a importar.

        Returns:
            ResultadoImportacion con el desglose de leídos, insertados y actualizados.
        """
        ruta = Path(ruta_archivo)
        if not str(ruta).strip():
            raise ErrorImportacionCarreras("La ruta del archivo no puede estar vacía.")

        try:
            carreras = self.lector.leer(ruta, nombre_hoja=nombre_hoja)
        except (FileNotFoundError, ValueError) as err:
            raise ErrorImportacionCarreras(f"Error al leer el archivo: {err}") from err
        except Exception as err:
            raise ErrorImportacionCarreras(f"Error inesperado al procesar el archivo Excel: {err}") from err

        total_leidos = len(carreras)
        if total_leidos == 0:
            return ResultadoImportacion(
                total_leidos=0,
                total_insertados=0,
                total_actualizados=0,
                ruta_archivo=str(ruta),
                mensaje="El archivo no contiene filas válidas de carreras para importar.",
            )

        try:
            insertados, actualizados = self.repositorio.guardar_muchas(carreras)
        except Exception as err:
            raise ErrorImportacionCarreras(
                f"Error al guardar las carreras en la base de datos: {err}"
            ) from err

        mensaje = (
            f"Importación completada: {total_leidos} carreras leídas, "
            f"{insertados} insertadas, {actualizados} actualizadas."
        )

        return ResultadoImportacion(
            total_leidos=total_leidos,
            total_insertados=insertados,
            total_actualizados=actualizados,
            ruta_archivo=str(ruta),
            mensaje=mensaje,
        )
