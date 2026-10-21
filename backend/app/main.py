from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.adapters.rutas_carreras import enrutador_carreras
from app.infrastructure.base_de_datos import crear_tablas


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa las tablas en SQLite al arrancar el servidor
    crear_tablas()
    yield


app = FastAPI(
    title="ORIENTA Compara MVP1",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "orienta-compara-mvp1"}


# Rutas de carreras
app.include_router(enrutador_carreras)
