from typing import Optional

from app.adapters.esquemas_carrera import CarreraRespuesta
from app.application.caso_uso_consultar_carreras import CasoUsoConsultarCarreras
from app.domain.carrera import Carrera


class CarrerasIgualesError(Exception):
    """Se lanza cuando se intenta comparar una carrera consigo misma."""


class CarreraNoEncontradaError(Exception):
    """Se lanza cuando una de las carreras solicitadas no existe."""


class CasoUsoCompararCarreras:
    """Caso de uso para comparar dos carreras del catalogo."""

    def __init__(self, caso_uso_consultar: CasoUsoConsultarCarreras) -> None:
        self.caso_uso_consultar = caso_uso_consultar

    def ejecutar(self, id_carrera_1: str, id_carrera_2: str):
        if not id_carrera_1 or not id_carrera_1.strip():
            raise CarreraNoEncontradaError("El identificador de la primera carrera es obligatorio.")
        if not id_carrera_2 or not id_carrera_2.strip():
            raise CarreraNoEncontradaError("El identificador de la segunda carrera es obligatorio.")

        id_norm_1 = CasoUsoConsultarCarreras.normalizar_id(id_carrera_1)
        id_norm_2 = CasoUsoConsultarCarreras.normalizar_id(id_carrera_2)

        if id_norm_1 == id_norm_2:
            raise CarrerasIgualesError("Las dos carreras a comparar deben ser distintas.")

        carrera_1 = self.caso_uso_consultar.obtener_por_id(id_carrera_1)
        if carrera_1 is None:
            raise CarreraNoEncontradaError(
                "Carrera con identificador '{}' no encontrada.".format(id_carrera_1)
            )

        carrera_2 = self.caso_uso_consultar.obtener_por_id(id_carrera_2)
        if carrera_2 is None:
            raise CarreraNoEncontradaError(
                "Carrera con identificador '{}' no encontrada.".format(id_carrera_2)
            )

        return self._construir_respuesta(carrera_1, carrera_2)

    @staticmethod
    def _diferencia_costo(carrera_1: Carrera, carrera_2: Carrera) -> Optional[float]:
        if carrera_1.costo_monto is None or carrera_2.costo_monto is None:
            return None
        return round(carrera_2.costo_monto - carrera_1.costo_monto, 2)

    def _construir_respuesta(self, carrera_1: Carrera, carrera_2: Carrera):
        from app.adapters.esquemas_comparacion import (
            ComparacionCarrerasRespuesta,
            CriterioComparacion,
        )

        criterios = [
            CriterioComparacion(
                criterio="Duracion (meses)",
                carrera_1="{} meses".format(carrera_1.duracion_meses),
                carrera_2="{} meses".format(carrera_2.duracion_meses),
            ),
            CriterioComparacion(
                criterio="Costo",
                carrera_1=carrera_1.costo_texto,
                carrera_2=carrera_2.costo_texto,
            ),
            CriterioComparacion(
                criterio="Modalidad",
                carrera_1=carrera_1.modalidad,
                carrera_2=carrera_2.modalidad,
            ),
            CriterioComparacion(
                criterio="Ubicacion",
                carrera_1=carrera_1.ubicacion,
                carrera_2=carrera_2.ubicacion,
            ),
            CriterioComparacion(
                criterio="Requisitos",
                carrera_1=carrera_1.requisitos,
                carrera_2=carrera_2.requisitos,
            ),
            CriterioComparacion(
                criterio="Campo laboral",
                carrera_1=carrera_1.campo_laboral,
                carrera_2=carrera_2.campo_laboral,
            ),
        ]

        return ComparacionCarrerasRespuesta(
            carrera_1=CarreraRespuesta.desde_dominio(carrera_1),
            carrera_2=CarreraRespuesta.desde_dominio(carrera_2),
            criterios=criterios,
            diferencia_duracion_meses=carrera_2.duracion_meses - carrera_1.duracion_meses,
            diferencia_costo=self._diferencia_costo(carrera_1, carrera_2),
            costo_es_rango_1=carrera_1.costo_es_rango,
            costo_es_rango_2=carrera_2.costo_es_rango,
            nota_datos=(
                "Los costos marcados como rango institucional son estimados a partir del rango "
                "publicado por la institucion; los costos fijos son valores verificados. "
                "Las fuentes y fechas de revision se incluyen en cada carrera."
            ),
        )
