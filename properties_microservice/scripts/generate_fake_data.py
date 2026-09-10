import os
import random
import time
from pathlib import Path

import mysql.connector
from faker import Faker
from dotenv import load_dotenv

# Carga .env para soportar ambos modos:
# 1) Host: scripts/.env (DB_HOST=localhost, DB_PORT=3307)
# 2) Docker/Root: .env en properties_microservice/ (DB_HOST=db_properties, DB_PORT=3306)
# Se intenta en orden, sin sobrescribir variables ya definidas.
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env", override=False)
load_dotenv(base_dir.parent / ".env", override=False)

fake = Faker(["es_ES", "es_MX"])

TOTAL_REGISTROS = 20000
TAMANO_LOTE = 5000
ESTADOS = ["ACTIVO", "INACTIVO"]


def get_connection(max_retries=30, delay=2):
    """Conecta a MySQL con reintentos - espera a que docker healthcheck pase."""
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", "3307")),
                database=os.getenv("DB_NAME", "properties_db"),
                user=os.getenv("DB_USER", "properties_user"),
                password=os.getenv("DB_PASSWORD", "properties_password"),
            )
            if attempt > 1:
                print(f"Conectado a MySQL en intento {attempt}")
            return conn
        except mysql.connector.Error as e:
            last_err = e
            print(f"[{attempt}/{max_retries}] MySQL no listo ({e}), reintentando en {delay}s...")
            time.sleep(delay)
    print(f"Error: no se pudo conectar a MySQL tras {max_retries} intentos")
    print(f"Verifica .env -> DB_HOST={os.getenv('DB_HOST')} DB_PORT={os.getenv('DB_PORT')} DB_NAME={os.getenv('DB_NAME')} DB_USER={os.getenv('DB_USER')}")
    raise last_err


def populate_data():
    conn = get_connection()
    cursor = conn.cursor()

    insert_propiedad = (
        "INSERT INTO propiedades (id_anfitrion, titulo, precio_noche, capacidad, estado) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    insert_ubicacion = (
        "INSERT INTO ubicaciones (id_propiedad, pais, ciudad, direccion) "
        "VALUES (%s, %s, %s, %s)"
    )

    print(f"Iniciando generación e inserción de {TOTAL_REGISTROS} propiedades...")

    for i in range(1, TOTAL_REGISTROS + 1, TAMANO_LOTE):
        lote = min(TAMANO_LOTE, TOTAL_REGISTROS - i + 1)

        propiedades = [(
            f"usuario-{random.randint(1, 5000)}",
            fake.sentence(nb_words=6).rstrip("."),
            round(random.uniform(20, 500), 2),
            random.randint(1, 12),
            random.choice(ESTADOS),
        ) for _ in range(lote)]

        cursor.executemany(insert_propiedad, propiedades)
        conn.commit()

        primer_id = cursor.lastrowid
        ubicaciones = [(
            primer_id + j,
            fake.country(),
            fake.city(),
            fake.street_address(),
        ) for j in range(lote)]

        cursor.executemany(insert_ubicacion, ubicaciones)
        conn.commit()

        print(f"{i + lote - 1} registros insertados...")

    print("Proceso de carga masiva completado con éxito.")
    cursor.close()
    conn.close()


if __name__ == "__main__":
    populate_data()
