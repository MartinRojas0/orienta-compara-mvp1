from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.adapters.esquemas_comparacion import (
    ComparacionCarrerasRespuesta,
    SolicitudComparacion,
)
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite
from app.application.caso_uso_comparar_carreras import (
    CarreraNoEncontradaError,
    CarrerasIgualesError,
    CasoUsoCompararCarreras,
)
from app.application.caso_uso_consultar_carreras import CasoUsoConsultarCarreras
from app.infrastructure.base_de_datos import obtener_sesion

enrutador_comparacion = APIRouter(prefix="/api", tags=["Comparación"])


def obtener_caso_uso_comparacion(
    sesion: Session = Depends(obtener_sesion),
) -> CasoUsoCompararCarreras:
    repositorio = RepositorioCarreraSQLite(sesion)
    caso_consultar = CasoUsoConsultarCarreras(repositorio)
    return CasoUsoCompararCarreras(caso_consultar)


@enrutador_comparacion.post(
    "/comparar",
    response_model=ComparacionCarrerasRespuesta,
    summary="Comparar dos carreras",
    description=(
        "Compara dos carreras del catálogo lado a lado en los criterios de duración, "
        "costo, modalidad, ubicación, requisitos y campo laboral."
    ),
    responses={
        200: {"description": "Comparación realizada correctamente"},
        400: {"description": "Las carreras a comparar deben ser distintas"},
        404: {"description": "Una de las carreras no existe"},
    },
)
def comparar_carreras(
    solicitud: SolicitudComparacion,
    caso_uso: CasoUsoCompararCarreras = Depends(obtener_caso_uso_comparacion),
):
    try:
        resultado = caso_uso.ejecutar(
            id_carrera_1=solicitud.id_carrera_1,
            id_carrera_2=solicitud.id_carrera_2,
        )
    except CarrerasIgualesError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    except CarreraNoEncontradaError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    return resultado
