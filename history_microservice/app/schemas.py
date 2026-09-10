from typing import List, Optional
from pydantic import BaseModel


class Huesped(BaseModel):
    id_usuario: str
    nombre: str
    email: str
    rol: Optional[str] = None
    fecha_registro: Optional[str] = None


class PropiedadResumen(BaseModel):
    id_propiedad: int
    titulo: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    direccion: Optional[str] = None
    estado: Optional[str] = None


class ViajeEnriquecido(BaseModel):
    id_reserva: str
    id_propiedad: int
    estado_reserva: Optional[str] = None
    tipo: str  # pasado | futuro | en_curso
    fecha_checkin: Optional[str] = None
    fecha_checkout: Optional[str] = None
    noches: int = 0
    precio_total: Optional[float] = None
    propiedad: Optional[PropiedadResumen] = None


class Stats(BaseModel):
    total_viajes: int = 0
    viajes_pasados: int = 0
    viajes_futuros: int = 0
    viajes_en_curso: int = 0
    noches_totales: int = 0
    gasto_total: float = 0.0
    ciudades_visitadas: List[str] = []
    proximo_viaje: Optional[ViajeEnriquecido] = None


class HistorialResponse(BaseModel):
    huesped: Huesped
    stats: Stats
    viajes: List[ViajeEnriquecido] = []


class ResumenResponse(BaseModel):
    huesped: Huesped
    stats: Stats
    proximo_viaje: Optional[ViajeEnriquecido] = None


class ReservaDetalle(BaseModel):
    id_reserva: str
    id_huesped: str
    id_propiedad: int
    fecha_checkin: Optional[str] = None
    fecha_checkout: Optional[str] = None
    precio_total: Optional[float] = None
    estado_reserva: Optional[str] = None
    fecha_creacion: Optional[str] = None


class DetalleReservaResponse(BaseModel):
    reserva: ReservaDetalle
    huesped: Huesped
    propiedad: Optional[PropiedadResumen] = None
