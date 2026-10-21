from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.rutas_carreras import enrutador_carreras
from app.adapters.rutas_comparacion import enrutador_comparacion
from app.infrastructure.base_de_datos import crear_tablas


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()
    yield


app = FastAPI(
    title="ORIENTA Compara MVP1 - API de Catálogo",
    description="API REST para consultar el catálogo de carreras universitarias.",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Carreras", "description": "Operaciones sobre el catálogo de carreras."},
        {"name": "Comparación", "description": "Comparación de carreras."},
        {"name": "Sistema", "description": "Endpoints de estado del servicio."},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Sistema"], summary="Estado del servicio")
def health():
    return {"status": "ok", "service": "orienta-compara-mvp1"}


app.include_router(enrutador_carreras)
app.include_router(enrutador_comparacion)
