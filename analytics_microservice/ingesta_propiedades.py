"""
Script de ingesta - Microservicio Analytics
Extrae el 100% de los registros de las tablas 'propiedades' y 'ubicaciones'
(MS2 - MySQL) y los sube como archivos CSV a un bucket S3.
"""

import csv
import io
import os

import boto3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.prod", override=False)

DB_HOST = os.getenv("DB_HOST_PRIVADO", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("DB_PORT_PROPERTIES", os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "properties_db")
DB_USER = os.getenv("DB_USER", "properties_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")

BUCKET_NAME = os.getenv("S3_BUCKET", "analytics-proyecto-cloud-utec-sec3")


def extraer_tabla(tabla: str):
    print(f"Conectando a MySQL para extraer '{tabla}'...")
    conn = mysql.connector.connect(
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = conn.cursor()

    print(f"Ejecutando SELECT * FROM {tabla}...")
    cursor.execute(f"SELECT * FROM {tabla};")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    print(f"Se extrajeron {len(rows)} registros de '{tabla}'.")

    cursor.close()
    conn.close()

    return colnames, rows


def convertir_a_csv(colnames, rows):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(colnames)
    writer.writerows(rows)
    return buffer.getvalue()


def subir_a_s3(csv_data: str, prefijo: str, nombre_archivo: str):
    print("Conectando a S3...")
    s3 = boto3.client("s3")
    key = f"{prefijo}/{nombre_archivo}"

    print(f"Subiendo archivo a s3://{BUCKET_NAME}/{key} ...")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_data.encode("utf-8"),
        ContentType="text/csv",
    )
    print(f"¡Subida completada! -> s3://{BUCKET_NAME}/{key}")


def procesar_tabla(tabla: str, prefijo: str, nombre_archivo: str):
    colnames, rows = extraer_tabla(tabla)
    if not rows:
        print(f"ADVERTENCIA: No se encontraron registros en '{tabla}'.")
        return
    csv_data = convertir_a_csv(colnames, rows)
    subir_a_s3(csv_data, prefijo, nombre_archivo)


def main():
    print("=" * 60)
    print("Iniciando ingesta de datos: Propiedades (MS2) -> S3")
    print("=" * 60)

    procesar_tabla("propiedades", "raw/propiedades", "propiedades.csv")
    procesar_tabla("ubicaciones", "raw/ubicaciones", "ubicaciones.csv")

    print("=" * 60)
    print("Proceso de ingesta finalizado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
