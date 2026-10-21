# ORIENTA Compara MVP1

Plataforma web para comparar opciones de orientación profesional (MVP 1).

## Stack

- **Backend:** FastAPI + SQLModel + Uvicorn (Python)
- **Frontend:** React + Vite + Tailwind CSS (`@tailwindcss/vite`)
- **Base de datos:** SQLite

## Arquitectura

Backend organizado con arquitectura híbrida (capa de presentación + estilo hexagonal):

```text
backend/app/
├── domain/          # Entidades y reglas de negocio
├── application/     # Casos de uso
├── adapters/        # Adaptadores de entrada/salida
├── infrastructure/  # Configuración, DB, etc.
└── main.py          # Punto de entrada FastAPI
```

## Instalación y ejecución

### Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend disponible en http://localhost:8000 (health: /health).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend disponible en http://localhost:5173.

## API de catálogo

Una vez levantado el backend, la documentación interactiva está disponible en:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Endpoints principales

- `GET /api/carreras` - Listado paginado con filtros opcionales.
- `GET /api/carreras/{id_carrera}` - Detalle de una carrera.
- `POST /api/carreras/importar` - Importa carreras desde Excel (uso administrativo).

### Ejemplos de uso

```bash
# Listado general (primeras 10)
curl "http://localhost:8000/api/carreras?limite=10&desplazamiento=0"

# Filtrar por institución y área de formación
curl "http://localhost:8000/api/carreras?institucion=UNI&area_formacion=Ingenieria"

# Filtrar por modalidad y ubicación
curl "http://localhost:8000/api/carreras?modalidad=Presencial&ubicacion=Lima%20Norte"

# Detalle de una carrera
curl "http://localhost:8000/api/carreras/C02"

# Carrera inexistente (404)
curl "http://localhost:8000/api/carreras/C999"
```

La respuesta de listado incluye `total`, `limite`, `desplazamiento` y `elementos`.

## Comparación de carreras

```bash
curl -X POST "http://localhost:8000/api/comparar" \
  -H "Content-Type: application/json" \
  -d '{"id_carrera_1":"C01","id_carrera_2":"C02"}'
```

Validaciones: IDs distintos (400 si son iguales) y existencia de ambas carreras (404 si alguna no existe).

La respuesta incluye los seis criterios lado a lado, diferencias numéricas de duración y costo, fuentes y fechas de revisión, y la indicación de datos estimados, verificados o no disponibles mediante `costo_es_rango`, `alcance_costo`, `costo_monto` y las fuentes asociadas.
