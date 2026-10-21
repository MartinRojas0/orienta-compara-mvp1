import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from app.adapters.esquemas_carrera import (
    CarreraRespuesta,
    ListaCarrerasRespuesta,
    RespuestaImportacion,
    SolicitudImportacion,
)
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite
from app.application.caso_uso_consultar_carreras import CasoUsoConsultarCarreras
from app.application.caso_uso_importar_carreras import (
    CasoUsoImportarCarreras,
    ErrorImportacionCarreras,
)
from app.infrastructure.base_de_datos import obtener_sesion

enrutador_carreras = APIRouter(prefix="/api/carreras", tags=["Carreras"])


def obtener_caso_uso_consulta(
    sesion: Session = Depends(obtener_sesion),
) -> CasoUsoConsultarCarreras:
    repositorio = RepositorioCarreraSQLite(sesion)
    return CasoUsoConsultarCarreras(repositorio)


def obtener_caso_uso_importacion(
    sesion: Session = Depends(obtener_sesion),
) -> CasoUsoImportarCarreras:
    repositorio = RepositorioCarreraSQLite(sesion)
    return CasoUsoImportarCarreras(repositorio)


@enrutador_carreras.get(
    "",
    response_model=ListaCarrerasRespuesta,
    summary="Listar carreras del cat?logo",
    description=(
        "Devuelve el listado paginado de carreras disponibles. "
        "Permite filtrar por instituci?n, ?rea de formaci?n, modalidad y ubicaci?n."
    ),
    responses={200: {"description": "Listado paginado de carreras"}},
)
def listar_carreras(
    institucion: Optional[str] = Query(None, description="Filtrar por sigla de institución (ej: UTP, UNI, UPN, UNMSM)"),
    area_formacion: Optional[str] = Query(None, description="Filtrar por área de formación (ej: Ingeniería, Negocios, Salud)"),
    modalidad: Optional[str] = Query(None, description="Filtrar por modalidad (ej: Presencial, Semipresencial)"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ubicacion (ej: Lima Norte, Lima Sur)"),
    limite: int = Query(100, ge=1, le=500, description="Cantidad máxima de registros a devolver"),
    desplazamiento: int = Query(0, ge=0, description="Número de registros a omitir para paginación"),
    caso_uso: CasoUsoConsultarCarreras = Depends(obtener_caso_uso_consulta),
):
    elementos = caso_uso.listar(
        institucion=institucion,
        area_formacion=area_formacion,
        modalidad=modalidad,
        ubicacion=ubicacion,
        limite=limite,
        desplazamiento=desplazamiento,
    )
    total = caso_uso.contar(
        institucion=institucion,
        area_formacion=area_formacion,
        modalidad=modalidad,
        ubicacion=ubicacion,
    )
    return ListaCarrerasRespuesta(
        total=total,
        limite=limite,
        desplazamiento=desplazamiento,
        elementos=[CarreraRespuesta.desde_dominio(c) for c in elementos],
    )


@enrutador_carreras.get(
    "/{id_carrera}",
    response_model=CarreraRespuesta,
    summary="Obtener detalle de una carrera",
    description="Devuelve el detalle completo de una carrera a partir de su identificador ?nico.",
    responses={
        200: {"description": "Detalle de la carrera"},
        404: {"description": "Carrera no encontrada"},
    },
)
def obtener_detalle_carrera(
    id_carrera: str,
    caso_uso: CasoUsoConsultarCarreras = Depends(obtener_caso_uso_consulta),
):
    carrera = caso_uso.obtener_por_id(id_carrera)
    if not carrera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Carrera con identificador '{id_carrera}' no encontrada.",
        )
    return CarreraRespuesta.desde_dominio(carrera)


@enrutador_carreras.post(
    "/importar",
    response_model=RespuestaImportacion,
    summary="Importar carreras desde archivo Excel a SQLite",
)
def importar_carreras(
    solicitud: Optional[SolicitudImportacion] = None,
    caso_uso: CasoUsoImportarCarreras = Depends(obtener_caso_uso_importacion),
):
    ruta = (solicitud.ruta_archivo if solicitud and solicitud.ruta_archivo else None) or os.getenv(
        "EXCEL_PATH", "data/ORIENTA_Lima_Norte_Ampliado.xlsx"
    )
    hoja = (solicitud.hoja if solicitud and solicitud.hoja else None) or "Carreras"

    try:
        resultado = caso_uso.ejecutar(ruta_archivo=ruta, nombre_hoja=hoja)
        return RespuestaImportacion(
            total_leidos=resultado.total_leidos,
            total_insertados=resultado.total_insertados,
            total_actualizados=resultado.total_actualizados,
            ruta_archivo=resultado.ruta_archivo,
            mensaje=resultado.mensaje,
        )
    except ErrorImportacionCarreras as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
