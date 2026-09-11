from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, crud
from .database import engine, get_db

# Crea las tablas en caso de que init.sql no se haya ejecutado
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gestión de Usuarios (Microservicio 1)",
    description="Microservicio de perfiles, autenticación y métodos de pago.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/usuarios/", response_model=schemas.UsuarioResponse)
def create_user(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    return crud.create_user(db=db, user=user)

@app.get("/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
def read_user(usuario_id: str, db: Session = Depends(get_db)):
    user = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@app.post("/usuarios/{usuario_id}/metodos-pago/", response_model=schemas.MetodoPagoResponse)
def create_metodo_pago(usuario_id: str, metodo: schemas.MetodoPagoCreate, db: Session = Depends(get_db)):
    # Validar que el usuario exista antes de añadir el método de pago
    user = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return crud.create_metodo_pago(db=db, metodo=metodo, id_usuario=usuario_id)


@app.post("/login/")
def login(credentials: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, email=credentials.email, password=credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")
    
    # El 'sub' (subject) es el estándar en JWT para identificar al usuario
    token_data = {"sub": str(user.id_usuario), "rol": user.rol}
    access_token = crud.create_access_token(data=token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario_id": user.id_usuario,
        "rol": user.rol
    }
