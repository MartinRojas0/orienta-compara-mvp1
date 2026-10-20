# ORIENTA Compara MVP1

Plataforma web para comparar opciones de orientación profesional (MVP 1).

## Stack

- **Backend:** FastAPI + SQLModel + Uvicorn (Python)
- **Frontend:** React + Vite + Tailwind CSS (`@tailwindcss/vite`)
- **Base de datos:** SQLite

## Arquitectura

Backend organizado con arquitectura híbrida (capa de presentación + estilo hexagonal):

```
backend/app/
+-- domain/          # Entidades y reglas de negocio
+-- application/     # Casos de uso
+-- adapters/        # Adaptadores de entrada/salida
+-- infrastructure/  # Configuración, DB, etc.
+-- main.py          # Punto de entrada FastAPI
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
