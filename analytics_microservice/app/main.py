"""MS5 Analytics — contrato stub.
Tu compañero reemplaza el modo MOCK por boto3+Athena real.
Contrato congelado: /health, /analytics/reservas-por-ciudad, /analytics/ocupacion-por-mes + /docs (swagger-ui).
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analytics Microservice", version="0.1.0-stub")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_MODE = os.getenv("ATHENA_MOCK", "true").lower() == "true"

@app.get("/health")
def health():
    return {"status": "ok", "mock": MOCK_MODE}

@app.get("/analytics/reservas-por-ciudad")
def reservas_por_ciudad():
    # TODO(compañero): query Athena sobre analytics_db.reservas
    return {
        "mock": MOCK_MODE,
        "data": [
            {"ciudad": "Lima", "total_reservas": 1250},
            {"ciudad": "Cusco", "total_reservas": 830},
        ],
    }

@app.get("/analytics/ocupacion-por-mes")
def ocupacion_por_mes():
    # TODO(compañero): query Athena con JOIN reservas+propiedades
    return {
        "mock": MOCK_MODE,
        "data": [
            {"mes": "2026-01", "ocupacion_pct": 72.5},
            {"mes": "2026-02", "ocupacion_pct": 68.1},
        ],
    }
