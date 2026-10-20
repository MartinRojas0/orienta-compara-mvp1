from typing import Optional
from sqlmodel import Field, SQLModel
from app.domain.carrera import Carrera


class CarreraDB(SQLModel, table=True):
    """Modelo de persistencia en base de datos SQLite para la entidad Carrera."""

    __tablename__ = "carreras"

    id_carrera: str = Field(primary_key=True, index=True)
    carrera: str = Field(index=True)
    institucion: str = Field(index=True)
    tipo_universidad: str = Field(index=True)
    duracion_meses: int
    modalidad: str = Field(index=True)
    ubicacion: str = Field(index=True)
    ambito_geografico: str
    costo_texto: str
    costo_minimo: Optional[float] = Field(default=None, index=True)
    costo_maximo: Optional[float] = Field(default=None, index=True)
    costo_monto: Optional[float] = Field(default=None, index=True)
    costo_es_rango: bool = Field(default=False)
    periodicidad_costo: str
    alcance_costo: str
    requisitos: str
    campo_laboral: str
    fuente_carrera: str
    fuente_costo: str
    fuente_requisitos: str
    fecha_revision: str
    fuente_duracion: str
    area_formacion: str = Field(index=True)
    grupo_carrera: str = Field(index=True)
    fuente_area: str
    criterio_area: str
    fuente_ubicacion: str

    # Codificación categórica auxiliar presente en el archivo Excel
    id_carrera_codigo: Optional[int] = Field(default=None)
    carrera_codigo: Optional[int] = Field(default=None)
    institucion_codigo: Optional[int] = Field(default=None)
    modalidad_codigo: Optional[int] = Field(default=None)
    ubicacion_codigo: Optional[int] = Field(default=None)
    requisitos_codigo: Optional[int] = Field(default=None)
    campo_laboral_codigo: Optional[int] = Field(default=None)
    fuente_carrera_codigo: Optional[int] = Field(default=None)
    fuente_costo_codigo: Optional[int] = Field(default=None)
    fuente_requisitos_codigo: Optional[int] = Field(default=None)
    fecha_revision_codigo: Optional[int] = Field(default=None)
    fuente_duracion_codigo: Optional[int] = Field(default=None)
    area_formacion_codigo: Optional[int] = Field(default=None)
    grupo_carrera_codigo: Optional[int] = Field(default=None)
    fuente_area_codigo: Optional[int] = Field(default=None)
    criterio_area_codigo: Optional[int] = Field(default=None)

    @classmethod
    def desde_dominio(cls, carrera: Carrera) -> "CarreraDB":
        return cls(
            id_carrera=carrera.id_carrera,
            carrera=carrera.carrera,
            institucion=carrera.institucion,
            tipo_universidad=carrera.tipo_universidad,
            duracion_meses=carrera.duracion_meses,
            modalidad=carrera.modalidad,
            ubicacion=carrera.ubicacion,
            ambito_geografico=carrera.ambito_geografico,
            costo_texto=carrera.costo_texto,
            costo_minimo=carrera.costo_minimo,
            costo_maximo=carrera.costo_maximo,
            costo_monto=carrera.costo_monto,
            costo_es_rango=carrera.costo_es_rango,
            periodicidad_costo=carrera.periodicidad_costo,
            alcance_costo=carrera.alcance_costo,
            requisitos=carrera.requisitos,
            campo_laboral=carrera.campo_laboral,
            fuente_carrera=carrera.fuente_carrera,
            fuente_costo=carrera.fuente_costo,
            fuente_requisitos=carrera.fuente_requisitos,
            fecha_revision=carrera.fecha_revision,
            fuente_duracion=carrera.fuente_duracion,
            area_formacion=carrera.area_formacion,
            grupo_carrera=carrera.grupo_carrera,
            fuente_area=carrera.fuente_area,
            criterio_area=carrera.criterio_area,
            fuente_ubicacion=carrera.fuente_ubicacion,
            id_carrera_codigo=carrera.id_carrera_codigo,
            carrera_codigo=carrera.carrera_codigo,
            institucion_codigo=carrera.institucion_codigo,
            modalidad_codigo=carrera.modalidad_codigo,
            ubicacion_codigo=carrera.ubicacion_codigo,
            requisitos_codigo=carrera.requisitos_codigo,
            campo_laboral_codigo=carrera.campo_laboral_codigo,
            fuente_carrera_codigo=carrera.fuente_carrera_codigo,
            fuente_costo_codigo=carrera.fuente_costo_codigo,
            fuente_requisitos_codigo=carrera.fuente_requisitos_codigo,
            fecha_revision_codigo=carrera.fecha_revision_codigo,
            fuente_duracion_codigo=carrera.fuente_duracion_codigo,
            area_formacion_codigo=carrera.area_formacion_codigo,
            grupo_carrera_codigo=carrera.grupo_carrera_codigo,
            fuente_area_codigo=carrera.fuente_area_codigo,
            criterio_area_codigo=carrera.criterio_area_codigo,
        )

    def a_dominio(self) -> Carrera:
        return Carrera(
            id_carrera=self.id_carrera,
            carrera=self.carrera,
            institucion=self.institucion,
            tipo_universidad=self.tipo_universidad,
            duracion_meses=self.duracion_meses,
            modalidad=self.modalidad,
            ubicacion=self.ubicacion,
            ambito_geografico=self.ambito_geografico,
            costo_texto=self.costo_texto,
            costo_minimo=self.costo_minimo,
            costo_maximo=self.costo_maximo,
            costo_monto=self.costo_monto,
            costo_es_rango=self.costo_es_rango,
            periodicidad_costo=self.periodicidad_costo,
            alcance_costo=self.alcance_costo,
            requisitos=self.requisitos,
            campo_laboral=self.campo_laboral,
            fuente_carrera=self.fuente_carrera,
            fuente_costo=self.fuente_costo,
            fuente_requisitos=self.fuente_requisitos,
            fecha_revision=self.fecha_revision,
            fuente_duracion=self.fuente_duracion,
            area_formacion=self.area_formacion,
            grupo_carrera=self.grupo_carrera,
            fuente_area=self.fuente_area,
            criterio_area=self.criterio_area,
            fuente_ubicacion=self.fuente_ubicacion,
            id_carrera_codigo=self.id_carrera_codigo,
            carrera_codigo=self.carrera_codigo,
            institucion_codigo=self.institucion_codigo,
            modalidad_codigo=self.modalidad_codigo,
            ubicacion_codigo=self.ubicacion_codigo,
            requisitos_codigo=self.requisitos_codigo,
            campo_laboral_codigo=self.campo_laboral_codigo,
            fuente_carrera_codigo=self.fuente_carrera_codigo,
            fuente_costo_codigo=self.fuente_costo_codigo,
            fuente_requisitos_codigo=self.fuente_requisitos_codigo,
            fecha_revision_codigo=self.fecha_revision_codigo,
            fuente_duracion_codigo=self.fuente_duracion_codigo,
            area_formacion_codigo=self.area_formacion_codigo,
            grupo_carrera_codigo=self.grupo_carrera_codigo,
            fuente_area_codigo=self.fuente_area_codigo,
            criterio_area_codigo=self.criterio_area_codigo,
        )
