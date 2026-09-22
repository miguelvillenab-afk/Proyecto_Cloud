"""MS5 Analytics — implementación real con boto3 + Athena.
Contrato: /health, /analytics/reservas-por-ciudad, /analytics/ocupacion-por-mes + /docs (swagger-ui).
"""
import os
import time

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Analytics Microservice", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_MODE = os.getenv("ATHENA_MOCK", "false").lower() == "true"

# --- Configuración de Athena ---
ATHENA_DB = os.getenv("ATHENA_DB", "analytics_db")
ATHENA_OUTPUT = os.getenv("ATHENA_OUTPUT", "s3://mvb-storage-s3/")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

athena_client = boto3.client("athena", region_name=AWS_REGION)


def ejecutar_consulta_athena(query: str):
    """Ejecuta una consulta SQL en Athena y devuelve los resultados como lista de diccionarios."""
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": ATHENA_DB},
        ResultConfiguration={"OutputLocation": ATHENA_OUTPUT},
    )
    query_execution_id = response["QueryExecutionId"]

    while True:
        status_response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = status_response["QueryExecution"]["Status"]["State"]

        if state == "SUCCEEDED":
            break
        elif state in ("FAILED", "CANCELLED"):
            reason = status_response["QueryExecution"]["Status"].get("StateChangeReason", "Sin detalle")
            raise HTTPException(status_code=500, detail=f"Consulta Athena falló: {reason}")

        time.sleep(0.5)

    results = athena_client.get_query_results(QueryExecutionId=query_execution_id)
    rows = results["ResultSet"]["Rows"]

    if not rows:
        return []

    columnas = [col.get("VarCharValue", "") for col in rows[0]["Data"]]
    datos = []
    for row in rows[1:]:
        valores = [col.get("VarCharValue", None) for col in row["Data"]]
        datos.append(dict(zip(columnas, valores)))

    return datos


@app.get("/health")
def health():
    return {"status": "ok", "mock": MOCK_MODE}


@app.get("/analytics/reservas-por-ciudad")
def reservas_por_ciudad():
    if MOCK_MODE:
        return {
            "mock": True,
            "data": [
                {"ciudad": "Lima", "total_reservas": 1250},
                {"ciudad": "Cusco", "total_reservas": 830},
            ],
        }

    query = """
        SELECT
            ub.ciudad,
            ub.pais,
            COUNT(r._id) AS total_reservas,
            SUM(r.precio_total) AS ingresos_totales
        FROM reservas r
        JOIN propiedades p ON CAST(r.id_propiedad AS bigint) = p.id_propiedad
        JOIN ubicaciones ub ON p.id_propiedad = ub.id_propiedad
        GROUP BY ub.ciudad, ub.pais
        ORDER BY total_reservas DESC
    """
    datos = ejecutar_consulta_athena(query)
    return {"mock": False, "data": datos}


@app.get("/analytics/ocupacion-por-mes")
def ocupacion_por_mes():
    if MOCK_MODE:
        return {
            "mock": True,
            "data": [
                {"mes": "2026-01", "ocupacion_pct": 72.5},
                {"mes": "2026-02", "ocupacion_pct": 68.1},
            ],
        }

    # "Ocupación" aproximada: cantidad de reservas por mes de check-in,
    # como proxy del nivel de actividad/ocupación de las propiedades.
    query = """
        SELECT
            substr(r.fecha_checkin, 1, 7) AS mes,
            COUNT(r._id) AS total_reservas
        FROM reservas r
        GROUP BY substr(r.fecha_checkin, 1, 7)
        ORDER BY mes
    """
    datos = ejecutar_consulta_athena(query)
    return {"mock": False, "data": datos}
