import os
import re
from pathlib import Path
from typing import Any, Optional
import openpyxl
from app.domain.carrera import Carrera

COLUMNAS_OBLIGATORIAS = [
    "id_carrera",
    "carrera",
    "institucion",
    "duracion_meses",
    "modalidad",
    "ubicacion",
    "costo_ensenanza_soles",
    "tipo_universidad",
]


class LectorCarrerasExcel:
    """Adaptador para la lectura y extracción de registros de carreras desde archivos Excel."""

    def __init__(self, nombre_hoja_predeterminada: str = "Carreras") -> None:
        self.nombre_hoja_predeterminada = nombre_hoja_predeterminada

    def leer(self, ruta_archivo: str | Path, nombre_hoja: Optional[str] = None) -> list[Carrera]:
        """Lee un archivo Excel y transforma sus filas en entidades Carrera de dominio.

        Args:
            ruta_archivo: Ruta al archivo .xlsx o .xls.
            nombre_hoja: Nombre opcional de la hoja a procesar. Si no se indica,
                         se buscará 'Carreras' o se utilizará la hoja activa.

        Returns:
            Lista de entidades Carrera validadas.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato es inválido o faltan columnas obligatorias.
        """
        ruta = Path(ruta_archivo)
        if not ruta.exists():
            raise FileNotFoundError(f"No se encontró el archivo Excel en la ruta: {ruta}")

        if ruta.suffix.lower() not in [".xlsx", ".xls", ".xlsm"]:
            raise ValueError(f"El archivo debe ser un libro de Excel (.xlsx, .xls). Extensión recibida: {ruta.suffix}")

        try:
            libro = openpyxl.load_workbook(str(ruta), data_only=True)
        except Exception as error:
            raise ValueError(f"Error al abrir el archivo Excel: {error}") from error

        hoja_seleccionada = None
        if nombre_hoja and nombre_hoja in libro.sheetnames:
            hoja_seleccionada = libro[nombre_hoja]
        elif self.nombre_hoja_predeterminada in libro.sheetnames:
            hoja_seleccionada = libro[self.nombre_hoja_predeterminada]
        else:
            hoja_seleccionada = libro.active

        if hoja_seleccionada is None:
            raise ValueError("No se pudo acceder a ninguna hoja válida en el archivo Excel.")

        # Obtener encabezados
        primera_fila = [celda.value for celda in hoja_seleccionada[1]]
        mapa_columnas: dict[str, int] = {}
        for indice, celda in enumerate(primera_fila, start=1):
            if celda is not None:
                clave = str(celda).strip()
                mapa_columnas[clave] = indice

        # Validar columnas obligatorias
        faltantes = [col for col in COLUMNAS_OBLIGATORIAS if col not in mapa_columnas]
        if faltantes:
            raise ValueError(f"El archivo Excel no contiene las columnas requeridas: {', '.join(faltantes)}")

        carreras: list[Carrera] = []

        for numero_fila in range(2, hoja_seleccionada.max_row + 1):
            # Verificar si la fila está vacía
            id_val = self._obtener_valor(hoja_seleccionada, numero_fila, mapa_columnas, "id_carrera")
            if not id_val or not str(id_val).strip():
                continue

            carrera = self._mapear_fila(hoja_seleccionada, numero_fila, mapa_columnas)
            carrera.validar()
            carreras.append(carrera)

        return carreras

    def _obtener_valor(
        self,
        hoja: Any,
        fila: int,
        mapa: dict[str, int],
        nombre_col: str,
    ) -> Any:
        col = mapa.get(nombre_col)
        if col is None:
            return None
        return hoja.cell(row=fila, column=col).value

    def _procesar_texto(self, valor: Any) -> str:
        if valor is None:
            return ""
        if hasattr(valor, "strftime"):
            return valor.strftime("%Y-%m-%d")
        return str(valor).strip()

    def _procesar_entero_opcional(self, valor: Any) -> Optional[int]:
        if valor is None or valor == "":
            return None
        try:
            return int(valor)
        except (ValueError, TypeError):
            return None

    def _procesar_costo(
        self, valor: Any
    ) -> tuple[str, Optional[float], Optional[float], Optional[float], bool]:
        """Procesa el campo costo_ensenanza_soles.

        Reglas:
        - Si es un rango (ej: '460–2605' o '460-2605'), separa en mínimo y máximo.
          NO fija un precio único para no convertir rangos institucionales en tarifas de una carrera.
        - Si es un número fijo (ej: 775 o 0 de gratuidad pública), mínimo, máximo y monto son iguales.
        - No regenera etiquetas de estado como 'estimado' o 'sin dato'.
        """
        if valor is None:
            return "", None, None, None, False

        valor_str = str(valor).strip()
        if not valor_str:
            return "", None, None, None, False

        # Comprobar si es un rango numérico separado por guion o raya en-dash/em-dash
        coincidencia_rango = re.match(
            r"^(\d+(?:\.\d+)?)\s*[\-–—]\s*(\d+(?:\.\d+)?)$", valor_str
        )
        if coincidencia_rango:
            costo_min = float(coincidencia_rango.group(1))
            costo_max = float(coincidencia_rango.group(2))
            # No inventar un precio fijo para rangos institucionales
            return valor_str, costo_min, costo_max, None, True

        # Comprobar si es un número directo (ej: 775 o 0)
        try:
            costo_num = float(valor)
            return valor_str, costo_num, costo_num, costo_num, False
        except (ValueError, TypeError):
            pass

        # Si viene en formato textual que no es número ni rango separable
        return valor_str, None, None, None, False

    def _mapear_fila(self, hoja: Any, fila: int, mapa: dict[str, int]) -> Carrera:
        id_carrera = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "id_carrera"))
        carrera_nombre = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "carrera"))
        institucion = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "institucion"))

        duracion_raw = self._obtener_valor(hoja, fila, mapa, "duracion_meses")
        try:
            duracion_meses = int(duracion_raw)
        except (ValueError, TypeError):
            raise ValueError(f"Fila {fila}: la duración en meses '{duracion_raw}' no es un número válido.")

        modalidad = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "modalidad"))
        ubicacion = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "ubicacion"))

        raw_costo = self._obtener_valor(hoja, fila, mapa, "costo_ensenanza_soles")
        costo_texto, costo_min, costo_max, costo_monto, es_rango = self._procesar_costo(raw_costo)

        requisitos = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "requisitos"))
        campo_laboral = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "campo_laboral"))
        fuente_carrera = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_carrera"))
        fuente_costo = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_costo"))
        fuente_requisitos = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_requisitos"))
        fecha_revision = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fecha_revision"))
        fuente_duracion = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_duracion"))
        area_formacion = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "area_formacion"))
        grupo_carrera = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "grupo_carrera"))
        fuente_area = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_area"))
        criterio_area = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "criterio_area"))
        tipo_universidad = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "tipo_universidad"))
        ambito_geografico = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "ambito_geografico"))
        periodicidad_costo = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "periodicidad_costo"))
        alcance_costo = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "alcance_costo"))
        fuente_ubicacion = self._procesar_texto(self._obtener_valor(hoja, fila, mapa, "fuente_ubicacion"))

        # Códigos numéricos auxiliares
        id_carrera_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "id_carrera_codigo"))
        carrera_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "carrera_codigo"))
        institucion_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "institucion_codigo"))
        modalidad_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "modalidad_codigo"))
        ubicacion_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "ubicacion_codigo"))
        requisitos_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "requisitos_codigo"))
        campo_laboral_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "campo_laboral_codigo"))
        fuente_carrera_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fuente_carrera_codigo"))
        fuente_costo_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fuente_costo_codigo"))
        fuente_requisitos_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fuente_requisitos_codigo"))
        fecha_revision_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fecha_revision_codigo"))
        fuente_duracion_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fuente_duracion_codigo"))
        area_formacion_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "area_formacion_codigo"))
        grupo_carrera_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "grupo_carrera_codigo"))
        fuente_area_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "fuente_area_codigo"))
        criterio_area_codigo = self._procesar_entero_opcional(self._obtener_valor(hoja, fila, mapa, "criterio_area_codigo"))

        return Carrera(
            id_carrera=id_carrera,
            carrera=carrera_nombre,
            institucion=institucion,
            duracion_meses=duracion_meses,
            modalidad=modalidad,
            ubicacion=ubicacion,
            costo_texto=costo_texto,
            requisitos=requisitos,
            campo_laboral=campo_laboral,
            fuente_carrera=fuente_carrera,
            fuente_costo=fuente_costo,
            fuente_requisitos=fuente_requisitos,
            fecha_revision=fecha_revision,
            fuente_duracion=fuente_duracion,
            area_formacion=area_formacion,
            grupo_carrera=grupo_carrera,
            fuente_area=fuente_area,
            criterio_area=criterio_area,
            tipo_universidad=tipo_universidad,
            ambito_geografico=ambito_geografico,
            periodicidad_costo=periodicidad_costo,
            alcance_costo=alcance_costo,
            fuente_ubicacion=fuente_ubicacion,
            costo_minimo=costo_min,
            costo_maximo=costo_max,
            costo_monto=costo_monto,
            costo_es_rango=es_rango,
            id_carrera_codigo=id_carrera_codigo,
            carrera_codigo=carrera_codigo,
            institucion_codigo=institucion_codigo,
            modalidad_codigo=modalidad_codigo,
            ubicacion_codigo=ubicacion_codigo,
            requisitos_codigo=requisitos_codigo,
            campo_laboral_codigo=campo_laboral_codigo,
            fuente_carrera_codigo=fuente_carrera_codigo,
            fuente_costo_codigo=fuente_costo_codigo,
            fuente_requisitos_codigo=fuente_requisitos_codigo,
            fecha_revision_codigo=fecha_revision_codigo,
            fuente_duracion_codigo=fuente_duracion_codigo,
            area_formacion_codigo=area_formacion_codigo,
            grupo_carrera_codigo=grupo_carrera_codigo,
            fuente_area_codigo=fuente_area_codigo,
            criterio_area_codigo=criterio_area_codigo,
        )
