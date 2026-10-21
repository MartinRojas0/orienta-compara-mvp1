# Carga de Carreras desde Excel a SQLite

Módulo encargado de la importación, validación, persistencia y consulta del catálogo de carreras universitarias para el proyecto ORIENTA Compara (MVP 1).

---

## 1. Arquitectura Hexagonal del Módulo

El backend organiza la funcionalidad de carreras desacoplando la lógica de negocio de las tecnologías de base de datos o lectura de archivos:

```
backend/
├── app/
│   ├── domain/               # Entidad pura Carrera y contrato RepositorioCarrera
│   ├── application/          # Casos de uso (CasoUsoImportarCarreras, CasoUsoConsultarCarreras)
│   ├── adapters/             # RepositorioCarreraSQLite, LectorCarrerasExcel, rutas FastAPI y esquemas
│   ├── infrastructure/       # Configuración y conexión SQLite (base_de_datos.py)
│   └── main.py               # Servidor FastAPI e inicialización de tablas
├── scripts/
│   └── cargar_carreras.py    # Script CLI para importación transaccional e idempotente
└── tests/                    # Pruebas automatizadas con pytest
data/
└── ORIENTA_Lima_Norte_Ampliado.xlsx  # Catálogo con 35 carreras universitarias
```

---

## 2. Dependencias del Backend

Instaladas en el entorno virtual (`backend/venv`) desde `backend/requirements.txt`:

- `fastapi==0.115.0`: Framework web para los endpoints REST.
- `sqlmodel==0.0.22`: Mapeo relacional en SQLite con modelos Pydantic/SQLAlchemy.
- `uvicorn[standard]==0.30.6`: Servidor ASGI para FastAPI.
- `openpyxl==3.1.5` y `pandas==2.2.2`: Lectura y procesamiento del archivo Excel.
- `python-dotenv==1.0.1`: Configuración mediante variables de entorno.
- `pytest>=8.0.0` y `httpx>=0.27.0`: Suite de pruebas unitarias y cliente de pruebas HTTP.

---

## 3. Carga de Datos desde Excel a SQLite

### Tratamiento de Datos y Reglas de Negocio

El archivo `data/ORIENTA_Lima_Norte_Ampliado.xlsx` contiene 35 carreras universitarias (UTP: 13, UNI: 9, UPN: 7, UNMSM: 6). El importador aplica las siguientes reglas:

1. **Idempotencia:** Utiliza el identificador de cada carrera (`id_carrera`, ej: `C01`, `C02`, ...) como clave estable. Ejecutar la carga múltiples veces no genera duplicados: actualiza los registros existentes.
2. **Transaccionalidad:** La carga completa se realiza dentro de una única transacción en la base de datos (si ocurre un fallo, revierte todo para evitar estados inconsistentes).
3. **Preservación de Costos sin Alteraciones:**
   - **Costos fijos (ej. UTP):** Se almacenan como valor numérico y texto (ej. `775`).
   - **Gratuidad en universidades públicas (UNI, UNMSM):** Se guarda con costo `0` y su respectivo alcance de gratuidad de primera carrera.
   - **Rangos institucionales (ej. UPN `460–2605` soles):** Se separan en `costo_minimo = 460.0` y `costo_maximo = 2605.0` con `costo_es_rango = True` y `costo_monto = None`. **No se asigna un precio fijo a carreras individuales** a partir de un tarifario global de cuotas.
4. **Fidelidad:** No se regeneran columnas de estado ni etiquetas inventadas como "estimado" o "sin dato". Se preservan todos los campos y códigos categóricos auxiliares.

### Ejecución del Script de Carga

Desde la raíz del proyecto o desde la carpeta `backend`:

```bash
# 1. Ejecutar con la ruta predeterminada (data/ORIENTA_Lima_Norte_Ampliado.xlsx):
python backend/scripts/cargar_carreras.py

# 2. O especificando una ruta alternativa:
python backend/scripts/cargar_carreras.py ruta/a/mi_archivo.xlsx

# Parámetros opcionales:
#   --hoja NOMBRE_HOJA   (por defecto: 'Carreras')
#   --db URL_SQLITE      (por defecto: toma DATABASE_URL del entorno o sqlite:///./orienta.db)
```

**Resumen emitido por consola:**
```text
==================================================
  ORIENTA - Importador de Carreras a SQLite
==================================================
Archivo Excel: ...\data\ORIENTA_Lima_Norte_Ampliado.xlsx
Hoja:          Carreras

--------------------------------------------------
  Resumen de la Importación
--------------------------------------------------
  • Registros leídos:       35
  • Registros insertados:   35
  • Registros actualizados: 0
--------------------------------------------------
[ÉXITO] Importación completada: 35 carreras leídas, 35 insertadas, 0 actualizadas.
```

---

## 4. Consulta de Carreras

### A. Mediante la API REST (FastAPI)

Inicia el servidor backend:

```bash
cd backend
uvicorn app.main:app --reload
```

El servidor estará en `http://localhost:8000`. La documentación interactiva Swagger se encuentra en `http://localhost:8000/docs`.

#### Endpoints disponibles:

- **`GET /api/carreras`**: Lista todas las carreras. Admite filtros opcionales por query params:
  - `institucion` (ej: `?institucion=UNI`, `?institucion=UTP`, `?institucion=UPN`)
  - `area_formacion` (ej: `?area_formacion=Ingeniería`, `?area_formacion=Negocios`, `?area_formacion=Salud`)
  - `modalidad` (ej: `?modalidad=Presencial`, `?modalidad=Semipresencial`)
  - `limite` y `desplazamiento` para paginación.
- **`GET /api/carreras/{id_carrera}`**: Detalle de una carrera con normalización flexible de identificadores:
  - Admite `C02`, `c02`, `02` o `2` (todos resuelven a la carrera `C02`).
  - Admite `C29`, `c29` o `29` (resuelven a la carrera `C29`).
- **`POST /api/carreras/importar`**: Permite disparar la importación mediante petición HTTP con cuerpo JSON opcional `{"ruta_archivo": "...", "hoja": "Carreras"}`.

### B. Mediante Código Python (Repositorio de Dominio)

```python
from sqlmodel import Session
from app.infrastructure.base_de_datos import motor
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite

with Session(motor) as sesion:
    repo = RepositorioCarreraSQLite(sesion)

    # Buscar por identificador
    carrera = repo.obtener_por_id("C01")
    print(carrera.carrera, carrera.institucion, carrera.costo_texto)

    # Filtrar por institución
    carreras_uni = repo.listar(institucion="UNI")
    print(f"Total UNI: {len(carreras_uni)}")
```

---

## 5. Ejecución de Pruebas Automatizadas

```bash
cd backend
venv\Scripts\activate
pytest -v tests
```

La suite [`backend/tests/test_carreras.py`](file:///C:/Users/Usuario/Downloads/Orienta-MVP1/backend/tests/test_carreras.py) cubre:
1. `test_importacion_archivo_real_y_comparacion_filas`: Cotejo fila por fila de las 35 carreras contra el Excel.
2. `test_idempotencia_importacion`: Ausencia total de duplicados tras ejecuciones repetidas.
3. `test_conservacion_rangos_y_costos`: Preservación de costos UTP, gratuidad UNI/UNMSM y rangos UPN sin tarifas inventadas.
4. `test_consultas_y_filtros_repositorio`: Búsquedas y filtros por universidad y área formativa.
5. `test_validacion_entidad_dominio`: Verificación de campos obligatorios en la entidad de negocio.
6. `test_error_archivo_inexistente`: Manejo controlado de errores con mensajes en español.
7. `test_endpoints_api`: Funcionamiento de `/health`, listado, filtros y normalización flexible de IDs en FastAPI.
