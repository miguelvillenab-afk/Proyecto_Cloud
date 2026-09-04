from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    rol = Column(String(20), nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now())

    # Relación uno a muchos con los métodos de pago
    metodos_pago = relationship("MetodoPago", back_populates="usuario", cascade="all, delete-orphan")

class MetodoPago(Base):
    __tablename__ = "metodos_pago"

    id_metodo = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(UUID(as_uuid=True), ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False)
    tipo_tarjeta = Column(String(50), nullable=False)
    ultimos_cuatro = Column(String(4), nullable=False)

    usuario = relationship("Usuario", back_populates="metodos_pago")
