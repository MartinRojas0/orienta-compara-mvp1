# ORIENTA Compara MVP1

Plataforma web para comparar opciones de orientación profesional y carreras universitarias (MVP 1).

## Stack Tecnológico

- **Backend:** FastAPI + SQLModel + Uvicorn (Python 3.11+)
- **Frontend:** React + Vite + Tailwind CSS (`@tailwindcss/vite`)
- **Base de datos:** SQLite
- **Librerías de procesamiento y pruebas:** openpyxl, pandas, pytest, httpx

## Arquitectura

El backend sigue los principios de la arquitectura hexagonal (puertos y adaptadores) para mantener el dominio completamente independiente de librerías externas:

```
backend/
├── app/
│   ├── domain/               # Entidades de negocio puras (Carrera) y contratos (RepositorioCarrera)
│   ├── application/          # Casos de uso (CasoUsoImportarCarreras, CasoUsoConsultarCarreras)
│   ├── adapters/             # Adaptadores de entrada/salida (RepositorioCarreraSQLite, LectorCarrerasExcel, rutas FastAPI)
│   ├── infrastructure/       # Configuración y conexión SQLite (base_de_datos.py)
│   └── main.py               # Punto de entrada de la aplicación FastAPI
├── scripts/
│   └── cargar_carreras.py    # Script CLI para la importación transaccional e idempotente
└── tests/                    # Suite de pruebas unitarias y de integración con pytest
data/
└── ORIENTA_Lima_Norte_Ampliado.xlsx  # Catálogo ampliado con 35 carreras universitarias
```

---

## Instalación y Configuración

### 1. Backend

```bash
cd backend
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Las dependencias principales instaladas desde `requirements.txt` incluyen:
- `fastapi==0.115.0`: Framework web de alto rendimiento.
- `sqlmodel==0.0.22`: ORM basado en SQLAlchemy y Pydantic.
- `uvicorn[standard]==0.30.6`: Servidor ASGI para FastAPI.
- `openpyxl==3.1.5` y `pandas==2.2.2`: Procesamiento y lectura de archivos Excel.
- `python-dotenv==1.0.1`: Carga de configuración desde variables de entorno.
- `pytest>=8.0.0` y `httpx>=0.27.0`: Ejecución de pruebas automatizadas y cliente HTTP de test.

---

## Carga de Datos desde Excel a SQLite

El proyecto incluye un importador que lee el archivo Excel, valida los campos obligatorios, persiste las carreras de forma transaccional e idempotente (evitando duplicados al usar `id_carrera` como clave estable) y conserva toda la información de costos:

- **Costos fijos (ej. UTP):** se almacenan con valor numérico y texto (ej. `775`).
- **Gratuidad en universidades públicas (UNI, UNMSM):** se guarda con valor `0` y alcance descriptivo.
- **Rangos institucionales (ej. UPN 460–2605 soles):** se dividen en `costo_minimo` (460.0) y `costo_maximo` (2605.0) con `costo_es_rango = True`, sin inventar tarifas fijas para carreras individuales.

### Ejecución del script de carga

Desde la raíz del proyecto o desde la carpeta `backend`:

```bash
# Ejecutar con el archivo predeterminado (data/ORIENTA_Lima_Norte_Ampliado.xlsx)
python backend/scripts/cargar_carreras.py

# O especificando una ruta alternativa:
python backend/scripts/cargar_carreras.py ruta/a/mi_archivo.xlsx

# Parámetros opcionales:
#   --hoja NOMBRE_HOJA   (por defecto: 'Carreras')
#   --db URL_SQLITE      (por defecto: toma DATABASE_URL del archivo .env o sqlite:///./orienta.db)
```

Al finalizar, el script reporta la cantidad de registros leídos, insertados y actualizados.

---

## Consultar los Datos

### 1. Mediante la API REST (FastAPI)

Inicia el servidor backend:

```bash
cd backend
uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`. Puedes explorar la documentación interactiva Swagger en:
- `http://localhost:8000/docs`

#### Endpoints disponibles:

- **`GET /health`**: Verificación de estado del servicio.
- **`GET /api/carreras`**: Lista todas las carreras disponibles. Admite filtros por query param:
  - `institucion` (ej. `?institucion=UNI`, `?institucion=UTP`)
  - `area_formacion` (ej. `?area_formacion=Ingeniería`, `?area_formacion=Negocios`)
  - `modalidad` (ej. `?modalidad=Presencial`, `?modalidad=Semipresencial`)
  - `limite` y `desplazamiento` para paginación.
- **`GET /api/carreras/{id_carrera}`**: Obtiene el detalle de una carrera específica por su identificador (ej. `/api/carreras/C01`, `/api/carreras/C29`).
- **`POST /api/carreras/importar`**: Permite ejecutar la carga desde el endpoint enviando un JSON opcional `{"ruta_archivo": "...", "hoja": "Carreras"}`.

### 2. Mediante el Repositorio en Python

```python
from sqlmodel import Session
from app.infrastructure.base_de_datos import motor
from app.adapters.repositorio_carrera_sqlite import RepositorioCarreraSQLite

with Session(motor) as sesion:
    repo = RepositorioCarreraSQLite(sesion)
    
    # Obtener carrera por identificador
    carrera = repo.obtener_por_id("C01")
    print(carrera.carrera, carrera.institucion, carrera.costo_texto)

    # Filtrar por institución
    carreras_uni = repo.listar(institucion="UNI")
    print(f"Total UNI: {len(carreras_uni)}")
```

---

## Ejecución de Pruebas

Para ejecutar la suite de pruebas automatizadas:

```bash
# Activar entorno virtual y ejecutar pytest
pytest -v backend/tests
```

Las pruebas verifican:
1. La importación de las **35 carreras** reales desde el archivo Excel ampliado y su coincidencia fila por fila.
2. La **idempotencia** de la carga en múltiples ejecuciones sucesivas (0 duplicados).
3. La correcta **conservación de costos y rangos** (UPN 460–2605, UTP 775, gratuidad UNI/UNMSM).
4. El funcionamiento del repositorio con filtros por institución, área y paginación.
5. La validación de negocio de la entidad `Carrera`.
6. El correcto funcionamiento de los endpoints HTTP en FastAPI.

---

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Disponible en `http://localhost:5173`.
