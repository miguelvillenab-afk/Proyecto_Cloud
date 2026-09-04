from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas

# Configuración para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def create_user(db: Session, user: schemas.UsuarioCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.Usuario(
        nombre=user.nombre,
        email=user.email,
        password_hash=hashed_password,
        rol=user.rol
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_metodo_pago(db: Session, metodo: schemas.MetodoPagoCreate, id_usuario: str):
    db_metodo = models.MetodoPago(**metodo.model_dump(), id_usuario=id_usuario)
    db.add(db_metodo)
    db.commit()
    db.refresh(db_metodo)
    return db_metodo
