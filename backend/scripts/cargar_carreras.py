#!/usr/bin/env python
"""Script de línea de comandos para importar carreras desde Excel a la base de datos SQLite."""

import argparse
import os
import sys
from pathlib import Path

# Asegurar que el directorio 'backend' esté en el sys.path
directorio_actual = Path(__file__).resolve().parent
directorio_backend = directorio_actual.parent
if str(directorio_backend) not in sys.path:
    sys.path.insert(0, str(directorio_backend))

from sqlmodel import Session
from app.adapters.lector_carreras_excel import LectorCarrerasExcel
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite
from app.application.caso_uso_importar_carreras import (
    CasoUsoImportarCarreras,
    ErrorImportacionCarreras,
)
from app.infrastructure.base_de_datos import crear_motor, crear_tablas


def buscar_ruta_predeterminada() -> str:
    """Busca la ubicación del archivo Excel predeterminado."""
    candidatas = [
        Path("data/ORIENTA_Lima_Norte_Ampliado.xlsx"),
        Path("../data/ORIENTA_Lima_Norte_Ampliado.xlsx"),
        directorio_backend.parent / "data" / "ORIENTA_Lima_Norte_Ampliado.xlsx",
        Path("ORIENTA_Lima_Norte_Ampliado.xlsx"),
    ]
    for candidata in candidatas:
        if candidata.exists():
            return str(candidata.resolve())
    return "data/ORIENTA_Lima_Norte_Ampliado.xlsx"


def parsear_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa las carreras desde un archivo Excel a la base de datos SQLite de forma transaccional e idempotente."
    )
    parser.add_argument(
        "ruta_excel",
        nargs="?",
        default=None,
        help="Ruta al archivo Excel (.xlsx). Si no se especifica, busca 'data/ORIENTA_Lima_Norte_Ampliado.xlsx'.",
    )
    parser.add_argument(
        "--hoja",
        dest="hoja",
        default="Carreras",
        help="Nombre de la hoja a procesar (por defecto: 'Carreras').",
    )
    parser.add_argument(
        "--db",
        "-d",
        dest="db_url",
        default=None,
        help="URL de conexión SQLite (por defecto: toma DATABASE_URL del entorno o sqlite:///./orienta.db).",
    )
    return parser.parse_args()


def main() -> int:
    args = parsear_argumentos()

    ruta_excel = args.ruta_excel or buscar_ruta_predeterminada()
    ruta_archivo = Path(ruta_excel).resolve()

    print("==================================================")
    print("  ORIENTA - Importador de Carreras a SQLite")
    print("==================================================")
    print(f"Archivo Excel: {ruta_archivo}")
    print(f"Hoja:          {args.hoja}")

    if not ruta_archivo.exists():
        print(f"\n[ERROR] No se encontró el archivo Excel en: {ruta_archivo}", file=sys.stderr)
        return 1

    try:
        motor = crear_motor(args.db_url)
        crear_tablas(motor)

        with Session(motor) as sesion:
            repo = RepositorioCarreraSQLite(sesion)
            lector = LectorCarrerasExcel(nombre_hoja_predeterminada=args.hoja)
            caso_uso = CasoUsoImportarCarreras(repositorio=repo, lector=lector)

            print("\nProcesando archivo...")
            resultado = caso_uso.ejecutar(ruta_archivo, nombre_hoja=args.hoja)

        print("\n--------------------------------------------------")
        print("  Resumen de la Importación")
        print("--------------------------------------------------")
        print(f"  • Registros leídos:       {resultado.total_leidos}")
        print(f"  • Registros insertados:   {resultado.total_insertados}")
        print(f"  • Registros actualizados: {resultado.total_actualizados}")
        print("--------------------------------------------------")
        print(f"[ÉXITO] {resultado.mensaje}\n")
        return 0

    except ErrorImportacionCarreras as err:
        print(f"\n[ERROR DE IMPORTACIÓN] {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"\n[ERROR INESPERADO] {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
