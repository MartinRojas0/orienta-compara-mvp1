from pathlib import Path

import pytest


def test_comparacion_exitosa(cliente_api, caso_uso_importar, ruta_excel_real: Path):
    caso_uso_importar.ejecutar(ruta_excel_real)

    resp = cliente_api.post(
        "/api/comparar",
        json={"id_carrera_1": "C01", "id_carrera_2": "C02"},
    )
    assert resp.status_code == 200
    datos = resp.json()
    assert datos["carrera_1"]["id_carrera"] == "C01"
    assert datos["carrera_2"]["id_carrera"] == "C02"
    assert len(datos["criterios"]) == 6
    assert datos["diferencia_duracion_meses"] == datos["carrera_2"]["duracion_meses"] - datos["carrera_1"]["duracion_meses"]


def test_comparacion_misma_carrera(cliente_api, caso_uso_importar, ruta_excel_real: Path):
    caso_uso_importar.ejecutar(ruta_excel_real)

    resp = cliente_api.post(
        "/api/comparar",
        json={"id_carrera_1": "C01", "id_carrera_2": "C01"},
    )
    assert resp.status_code == 400
    assert "distintas" in resp.json()["detail"]


def test_comparacion_variante_misma_carrera(cliente_api, caso_uso_importar, ruta_excel_real: Path):
    caso_uso_importar.ejecutar(ruta_excel_real)

    resp = cliente_api.post(
        "/api/comparar",
        json={"id_carrera_1": "1", "id_carrera_2": "01"},
    )
    assert resp.status_code == 400


def test_comparacion_carrera_inexistente(cliente_api, caso_uso_importar, ruta_excel_real: Path):
    caso_uso_importar.ejecutar(ruta_excel_real)

    resp = cliente_api.post(
        "/api/comparar",
        json={"id_carrera_1": "C01", "id_carrera_2": "C999"},
    )
    assert resp.status_code == 404
    assert "no encontrada" in resp.json()["detail"]
