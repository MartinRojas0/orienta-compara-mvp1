from typing import Optional
from pydantic import BaseModel, Field

from app.adapters.esquemas_carrera import CarreraRespuesta


class SolicitudComparacion(BaseModel):
    """Esquema de entrada para la comparacion de dos carreras."""

    id_carrera_1: str = Field(..., min_length=1, description="Identificador de la primera carrera (ej: C01)")
    id_carrera_2: str = Field(..., min_length=1, description="Identificador de la segunda carrera (ej: C02)")


class CriterioComparacion(BaseModel):
    """Representa un criterio comparado entre ambas carreras."""

    criterio: str
    carrera_1: str
    carrera_2: str


class ComparacionCarrerasRespuesta(BaseModel):
    """Esquema de respuesta de la comparacion de dos carreras."""

    carrera_1: CarreraRespuesta
    carrera_2: CarreraRespuesta
    criterios: list[CriterioComparacion]
    diferencia_duracion_meses: int
    diferencia_costo: Optional[float] = None
    costo_es_rango_1: bool
    costo_es_rango_2: bool
    nota_datos: str
