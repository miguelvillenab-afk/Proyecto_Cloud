import os
import sys
import random

# Añadir el directorio raíz al path para importar la app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from faker import Faker
from app.models import Usuario
from dotenv import load_dotenv

load_dotenv()

# Usar la variable de entorno configurada
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake = Faker()

def populate_data():
    db = SessionLocal()
    print("Iniciando generación e inserción de 20,000 registros de usuarios...")
    
    usuarios_batch = []
    roles = ['HUESPED', 'ANFITRION']
    
    for i in range(1, 20001):
        usuarios_batch.append(
            Usuario(
                nombre=fake.name(),
                email=fake.unique.email(),
                password_hash=fake.sha256(), # Hash simulado por velocidad
                rol=random.choice(roles)
            )
        )
        
        # Insertar en bloques de 5,000 para optimizar el rendimiento
        if len(usuarios_batch) == 5000:
            db.bulk_save_objects(usuarios_batch)
            db.commit()
            print(f"{i} registros insertados...")
            usuarios_batch = []
            
    print("Proceso de carga masiva completado con éxito.")
    db.close()

if __name__ == "__main__":
    populate_data()
