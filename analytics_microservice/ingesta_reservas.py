"""
Script de ingesta - Microservicio Analytics
Extrae el 100% de los registros de las colecciones 'reservas' y 'resenas'
(MS3 - MongoDB) y los sube como archivos JSON Lines a un bucket S3.
"""

import io
import json
import os
from datetime import datetime, date

import boto3
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
load_dotenv(".env.prod", override=False)

DB_HOST = os.getenv("DB_HOST_PRIVADO", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("DB_PORT_RESERVATIONS", os.getenv("DB_PORT", "27017"))
DB_NAME = os.getenv("MONGO_DB", "reservations_db")

BUCKET_NAME = os.getenv("S3_BUCKET", "analytics-proyecto-cloud-utec-sec3")


def limpiar_valor(v):
    """Convierte tipos de Mongo (ObjectId, datetime) a texto plano."""
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v


def documento_a_dict(doc):
    return {k: limpiar_valor(v) for k, v in doc.items()}


def extraer_coleccion(nombre: str):
    print(f"Conectando a MongoDB para extraer '{nombre}'...")
    uri = f"mongodb://{DB_HOST}:{DB_PORT}/"
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]

    print(f"Leyendo colección '{nombre}'...")
    docs = list(db[nombre].find({}))
    print(f"Se extrajeron {len(docs)} documentos de '{nombre}'.")

    client.close()
    return docs


def convertir_a_jsonl(docs):
    buffer = io.StringIO()
    for doc in docs:
        limpio = documento_a_dict(doc)
        buffer.write(json.dumps(limpio, ensure_ascii=False))
        buffer.write("\n")
    return buffer.getvalue()


def subir_a_s3(data: str, prefijo: str, nombre_archivo: str):
    print("Conectando a S3...")
    s3 = boto3.client("s3")
    key = f"{prefijo}/{nombre_archivo}"

    print(f"Subiendo archivo a s3://{BUCKET_NAME}/{key} ...")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=data.encode("utf-8"),
        ContentType="application/json",
    )
    print(f"¡Subida completada! -> s3://{BUCKET_NAME}/{key}")


def procesar_coleccion(nombre: str, prefijo: str, nombre_archivo: str):
    docs = extraer_coleccion(nombre)
    if not docs:
        print(f"ADVERTENCIA: No se encontraron documentos en '{nombre}'.")
        return
    data = convertir_a_jsonl(docs)
    subir_a_s3(data, prefijo, nombre_archivo)


def main():
    print("=" * 60)
    print("Iniciando ingesta de datos: Reservas (MS3) -> S3")
    print("=" * 60)

    procesar_coleccion("reservas", "raw/reservas", "reservas.jsonl")
    procesar_coleccion("resenas", "raw/resenas", "resenas.jsonl")

    print("=" * 60)
    print("Proceso de ingesta finalizado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
