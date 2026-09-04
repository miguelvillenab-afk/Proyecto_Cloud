from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime
from uuid import UUID

# --- Esquemas de Método de Pago ---
class MetodoPagoBase(BaseModel):
    tipo_tarjeta: str
    ultimos_cuatro: str

class MetodoPagoCreate(MetodoPagoBase):
    pass

class MetodoPagoResponse(MetodoPagoBase):
    id_metodo: int
    id_usuario: UUID

    class Config:
        from_attributes = True

# --- Esquemas de Usuario ---
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr
    rol: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioResponse(UsuarioBase):
    id_usuario: UUID
    fecha_registro: datetime
    metodos_pago: List[MetodoPagoResponse] = []

    class Config:
        from_attributes = True
