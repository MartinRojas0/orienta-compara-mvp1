from typing import Optional
from sqlmodel import Session, col, func, select
from app.adapters.modelo_carrera import CarreraDB
from app.domain.carrera import Carrera
from app.domain.repositorio_carrera import RepositorioCarrera


class RepositorioCarreraSQLite(RepositorioCarrera):
    """Implementación SQLite del repositorio de carreras utilizando SQLModel."""

    def __init__(self, sesion: Session) -> None:
        self.sesion = sesion

    def guardar(self, carrera: Carrera) -> Carrera:
        """Guarda o actualiza una carrera individual."""
        carrera.validar()
        existente = self.sesion.get(CarreraDB, carrera.id_carrera)
        if existente:
            datos = CarreraDB.desde_dominio(carrera)
            for clave, valor in datos.model_dump(exclude={"id_carrera"}).items():
                setattr(existente, clave, valor)
            self.sesion.add(existente)
            self.sesion.commit()
            self.sesion.refresh(existente)
            return existente.a_dominio()

        nuevo = CarreraDB.desde_dominio(carrera)
        self.sesion.add(nuevo)
        self.sesion.commit()
        self.sesion.refresh(nuevo)
        return nuevo.a_dominio()

    def guardar_muchas(self, carreras: list[Carrera]) -> tuple[int, int]:
        """Guarda o actualiza múltiples carreras de forma transaccional.

        Retorna (insertados, actualizados).
        Si ocurre un error durante el proceso, revierte la transacción.
        """
        insertados = 0
        actualizados = 0

        try:
            for carrera in carreras:
                carrera.validar()
                existente = self.sesion.get(CarreraDB, carrera.id_carrera)
                if existente:
                    datos = CarreraDB.desde_dominio(carrera)
                    for clave, valor in datos.model_dump(exclude={"id_carrera"}).items():
                        setattr(existente, clave, valor)
                    self.sesion.add(existente)
                    actualizados += 1
                else:
                    nuevo = CarreraDB.desde_dominio(carrera)
                    self.sesion.add(nuevo)
                    insertados += 1
            self.sesion.commit()
            return insertados, actualizados
        except Exception:
            self.sesion.rollback()
            raise

    def obtener_por_id(self, id_carrera: str) -> Optional[Carrera]:
        """Obtiene una carrera por su identificador primario."""
        registro = self.sesion.get(CarreraDB, id_carrera)
        if not registro:
            return None
        return registro.a_dominio()

    def listar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
        limite: int = 100,
        desplazamiento: int = 0,
    ) -> list[Carrera]:
        """Lista las carreras almacenadas con soporte de filtros opcionales."""
        consulta = select(CarreraDB)

        if institucion:
            consulta = consulta.where(CarreraDB.institucion == institucion)
        if area_formacion:
            consulta = consulta.where(CarreraDB.area_formacion == area_formacion)
        if modalidad:
            consulta = consulta.where(CarreraDB.modalidad == modalidad)

        consulta = consulta.order_by(col(CarreraDB.id_carrera)).offset(desplazamiento).limit(limite)
        registros = self.sesion.exec(consulta).all()
        return [reg.a_dominio() for reg in registros]

    def contar(
        self,
        institucion: Optional[str] = None,
        area_formacion: Optional[str] = None,
        modalidad: Optional[str] = None,
    ) -> int:
        """Cuenta la cantidad total de carreras que cumplen los criterios."""
        consulta = select(func.count(col(CarreraDB.id_carrera)))

        if institucion:
            consulta = consulta.where(CarreraDB.institucion == institucion)
        if area_formacion:
            consulta = consulta.where(CarreraDB.area_formacion == area_formacion)
        if modalidad:
            consulta = consulta.where(CarreraDB.modalidad == modalidad)

        total = self.sesion.exec(consulta).one()
        return int(total)

    def existe_por_id(self, id_carrera: str) -> bool:
        """Verifica la existencia previa de una carrera."""
        return self.sesion.get(CarreraDB, id_carrera) is not None
