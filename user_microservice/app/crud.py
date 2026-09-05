from sqlalchemy.orm import Session
from passlib.context import CryptContext
from . import models, schemas
import jwt
import os
from datetime import datetime, timedelta

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

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def create_access_token(data: dict):
    to_encode = data.copy()
    # Tiempo de expiración del token
    expire_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    
    # Firma del token usando la clave secreta del .env
    encoded_jwt = jwt.encode(
        to_encode, 
        os.getenv("JWT_SECRET_KEY", "clave_por_defecto_local"), 
        algorithm=os.getenv("JWT_ALGORITHM", "HS256")
    )
    return encoded_jwt
