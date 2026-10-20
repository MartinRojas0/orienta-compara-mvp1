from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.domain.carrera import Carrera


class CarreraRespuesta(BaseModel):
    """Esquema de respuesta para los datos de una carrera."""

    model_config = ConfigDict(from_attributes=True)

    id_carrera: str
    carrera: str
    institucion: str
    tipo_universidad: str
    duracion_meses: int
    modalidad: str
    ubicacion: str
    ambito_geografico: str
    costo_texto: str
    costo_minimo: Optional[float] = None
    costo_maximo: Optional[float] = None
    costo_monto: Optional[float] = None
    costo_es_rango: bool
    periodicidad_costo: str
    alcance_costo: str
    requisitos: str
    campo_laboral: str
    fuente_carrera: str
    fuente_costo: str
    fuente_requisitos: str
    fecha_revision: str
    fuente_duracion: str
    area_formacion: str
    grupo_carrera: str
    fuente_area: str
    criterio_area: str
    fuente_ubicacion: str

    # Códigos numéricos auxiliares
    id_carrera_codigo: Optional[int] = None
    carrera_codigo: Optional[int] = None
    institucion_codigo: Optional[int] = None
    modalidad_codigo: Optional[int] = None
    ubicacion_codigo: Optional[int] = None
    requisitos_codigo: Optional[int] = None
    campo_laboral_codigo: Optional[int] = None
    fuente_carrera_codigo: Optional[int] = None
    fuente_costo_codigo: Optional[int] = None
    fuente_requisitos_codigo: Optional[int] = None
    fecha_revision_codigo: Optional[int] = None
    fuente_duracion_codigo: Optional[int] = None
    area_formacion_codigo: Optional[int] = None
    grupo_carrera_codigo: Optional[int] = None
    fuente_area_codigo: Optional[int] = None
    criterio_area_codigo: Optional[int] = None

    @classmethod
    def desde_dominio(cls, carrera: Carrera) -> "CarreraRespuesta":
        return cls(**carrera.__dict__)


class ListaCarrerasRespuesta(BaseModel):
    """Esquema paginado de listado de carreras."""

    total: int
    limite: int
    desplazamiento: int
    elementos: list[CarreraRespuesta]


class SolicitudImportacion(BaseModel):
    """Esquema para solicitar la importación vía endpoint."""

    ruta_archivo: Optional[str] = None
    hoja: Optional[str] = "Carreras"


class RespuestaImportacion(BaseModel):
    """Esquema de respuesta tras la ejecución de la importación."""

    total_leidos: int
    total_insertados: int
    total_actualizados: int
    ruta_archivo: str
    mensaje: str
