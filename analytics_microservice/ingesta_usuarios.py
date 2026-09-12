"""
Script de ingesta - Microservicio Analytics
Extrae el 100% de los registros de la tabla 'usuarios' (MS1 - PostgreSQL)
y los sube como archivo CSV a un bucket S3.
"""

import csv
import io
import os
from datetime import datetime, timezone

import boto3
import psycopg2
from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.prod", override=False)

# Local por defecto (localhost:5433), en AWS usa .env.prod (172.31.21.204:5432).
DB_HOST = os.getenv("DB_HOST_PRIVADO", os.getenv("DB_HOST", "localhost"))
DB_PORT = os.getenv("DB_PORT_USERS", os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("POSTGRES_DB", "users_db")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secretpassword")

# Configuración de S3
BUCKET_NAME = os.getenv("S3_BUCKET", "analytics-proyecto-cloud-aguirre")
S3_PREFIX = os.getenv("S3_PREFIX_USUARIOS", "raw/usuarios")


def extraer_usuarios():
    """Conecta a PostgreSQL y extrae todos los registros de la tabla usuarios."""
    print("Conectando a PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = conn.cursor()

    print("Ejecutando SELECT * FROM usuarios...")
    cursor.execute("SELECT * FROM usuarios;")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]

    print(f"Se extrajeron {len(rows)} registros.")

    cursor.close()
    conn.close()

    return colnames, rows


def convertir_a_csv(colnames, rows):
    """Convierte los datos extraídos a formato CSV en memoria."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(colnames)
    writer.writerows(rows)
    return buffer.getvalue()


def subir_a_s3(csv_data):
    """Sube el CSV generado a S3."""
    print("Conectando a S3...")
    s3 = boto3.client("s3")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    key = f"{S3_PREFIX}/usuarios_{timestamp}.csv"

    print(f"Subiendo archivo a s3://{BUCKET_NAME}/{key} ...")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=csv_data.encode("utf-8"),
        ContentType="text/csv",
    )

    print("¡Subida completada con éxito!")
    print(f"Archivo disponible en: s3://{BUCKET_NAME}/{key}")


def main():
    print("=" * 60)
    print("Iniciando ingesta de datos: Usuarios (MS1) -> S3")
    print("=" * 60)

    colnames, rows = extraer_usuarios()

    if not rows:
        print("ADVERTENCIA: No se encontraron registros para extraer.")
        return

    csv_data = convertir_a_csv(colnames, rows)
    subir_a_s3(csv_data)

    print("=" * 60)
    print("Proceso de ingesta finalizado.")
    print("=" * 60)


if __name__ == "__main__":
    main()
