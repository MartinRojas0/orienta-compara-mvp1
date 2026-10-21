from dataclasses import dataclass
from typing import Optional


@dataclass
class Carrera:
    """Entidad de dominio que representa una carrera universitaria u opción formativa."""

    id_carrera: str
    carrera: str
    institucion: str
    duracion_meses: int
    modalidad: str
    ubicacion: str
    costo_texto: str
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
    tipo_universidad: str
    ambito_geografico: str
    periodicidad_costo: str
    alcance_costo: str
    fuente_ubicacion: str
    costo_minimo: Optional[float] = None
    costo_maximo: Optional[float] = None
    costo_monto: Optional[float] = None
    costo_es_rango: bool = False
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

    def validar(self) -> None:
        """Valida que los campos obligatorios del negocio contengan información válida."""
        if not self.id_carrera or not self.id_carrera.strip():
            raise ValueError("El identificador de la carrera (id_carrera) es obligatorio.")
        if not self.carrera or not self.carrera.strip():
            raise ValueError(f"El nombre de la carrera es obligatorio para {self.id_carrera}.")
        if not self.institucion or not self.institucion.strip():
            raise ValueError(f"La institución es obligatoria para {self.id_carrera}.")
        if self.duracion_meses is None or self.duracion_meses <= 0:
            raise ValueError(f"La duración en meses debe ser un entero positivo para {self.id_carrera}.")
        if not self.modalidad or not self.modalidad.strip():
            raise ValueError(f"La modalidad es obligatoria para {self.id_carrera}.")
        if not self.ubicacion or not self.ubicacion.strip():
            raise ValueError(f"La ubicación es obligatoria para {self.id_carrera}.")
        if not self.tipo_universidad or not self.tipo_universidad.strip():
            raise ValueError(f"El tipo de universidad es obligatorio para {self.id_carrera}.")
        if not self.costo_texto or not self.costo_texto.strip():
            raise ValueError(f"El costo de enseñanza es obligatorio para {self.id_carrera}.")
