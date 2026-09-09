import os
import random

import mysql.connector
from faker import Faker
from dotenv import load_dotenv

load_dotenv()

fake = Faker(["es_ES", "es_MX"])

TOTAL_REGISTROS = 20000
TAMANO_LOTE = 5000
ESTADOS = ["ACTIVO", "INACTIVO"]


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3307")),
        database=os.getenv("DB_NAME", "properties_db"),
        user=os.getenv("DB_USER", "properties_user"),
        password=os.getenv("DB_PASSWORD", "changeme"),
    )


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
