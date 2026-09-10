import asyncio
from datetime import date, datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import services
from .services import ExternalServiceError
from .schemas import (
    DetalleReservaResponse,
    Huesped,
    HistorialResponse,
    PropiedadResumen,
    ReservaDetalle,
    ResumenResponse,
    Stats,
    ViajeEnriquecido,
)

app = FastAPI(
    title="Historial de Viajes del Huesped (Microservicio 4)",
    description=(
        "Agregador sin BD propia. Consulta MS1 (Usuarios), "
        "MS3 (Reservas) y MS2 (Catalogo) para devolver la Historia del Viajero."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Helpers puros (sin I/O) ---

def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def _calc_noches(checkin, checkout) -> int:
    d1, d2 = _parse_date(checkin), _parse_date(checkout)
    if d1 is None or d2 is None:
        return 0
    return max((d2 - d1).days, 0)


def _clasificar(checkin, checkout) -> str:
    hoy = date.today()
    d1, d2 = _parse_date(checkin), _parse_date(checkout)
    if d1 is None or d2 is None:
        return "pasado"
    if d1 > hoy:
        return "futuro"
    if d2 < hoy:
        return "pasado"
    return "en_curso"


def _build_huesped(raw: dict) -> Huesped:
    return Huesped(
        id_usuario=str(raw.get("id_usuario", "")),
        nombre=raw.get("nombre", ""),
        email=raw.get("email", ""),
        rol=raw.get("rol"),
        fecha_registro=str(raw.get("fecha_registro")) if raw.get("fecha_registro") else None,
    )


def _build_propiedad(id_propiedad: int, raw: dict | None) -> PropiedadResumen | None:
    if raw is None:
        return None
    ubi = raw.get("ubicacion") or raw.get("location") or {}
    return PropiedadResumen(
        id_propiedad=id_propiedad,
        titulo=raw.get("titulo"),
        ciudad=ubi.get("ciudad"),
        pais=ubi.get("pais"),
        direccion=ubi.get("direccion"),
        estado=raw.get("estado"),
    )


def _reserva_id(raw: dict) -> str:
    return str(raw.get("_id") or raw.get("id") or "")


def _enrich_reserva(raw: dict, prop_raw: dict | None) -> ViajeEnriquecido:
    checkin = raw.get("fecha_checkin")
    checkout = raw.get("fecha_checkout")
    id_prop = int(raw.get("id_propiedad"))
    return ViajeEnriquecido(
        id_reserva=_reserva_id(raw),
        id_propiedad=id_prop,
        estado_reserva=raw.get("estado_reserva"),
        tipo=_clasificar(checkin, checkout),
        fecha_checkin=str(checkin)[:10] if checkin else None,
        fecha_checkout=str(checkout)[:10] if checkout else None,
        noches=_calc_noches(checkin, checkout),
        precio_total=raw.get("precio_total"),
        propiedad=_build_propiedad(id_prop, prop_raw),
    )


def _build_stats(viajes: list[ViajeEnriquecido]) -> Stats:
    validos = [v for v in viajes if v.estado_reserva != "CANCELADA"]
    ciudades = sorted({v.propiedad.ciudad for v in validos if v.propiedad and v.propiedad.ciudad})
    futuros = sorted(
        [v for v in viajes if v.tipo == "futuro"],
        key=lambda v: v.fecha_checkin or "",
    )
    return Stats(
        total_viajes=len(viajes),
        viajes_pasados=sum(1 for v in viajes if v.tipo == "pasado"),
        viajes_futuros=sum(1 for v in viajes if v.tipo == "futuro"),
        viajes_en_curso=sum(1 for v in viajes if v.tipo == "en_curso"),
        noches_totales=sum(v.noches for v in validos),
        gasto_total=round(sum((v.precio_total or 0) for v in validos), 2),
        ciudades_visitadas=ciudades,
        proximo_viaje=futuros[0] if futuros else None,
    )


async def _fetch_propiedades(ids: set[int]) -> dict[int, dict | None]:
    async def _one(pid: int):
        try:
            return pid, await services.get_propiedad(pid)
        except ExternalServiceError:
            return pid, None

    results = await asyncio.gather(*[_one(pid) for pid in ids])
    return dict(results)


def _handle_external(err: ExternalServiceError):
    raise HTTPException(status_code=err.status_code, detail=err.message)


# --- Endpoints ---

@app.get("/")
def root():
    return {
        "servicio": "historial-viajes-huesped",
        "descripcion": "Agregador sin BD: historia del viajero (MS1 + MS3 + MS2)",
        "version": "1.0.0",
        "endpoints": [
            "GET /health",
            "GET /historial/{id_usuario}",
            "GET /historial/{id_usuario}/resumen",
            "GET /historial/reserva/{id_reserva}",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# IMPORTANTE: esta ruta debe ir ANTES de /historial/{id_usuario}
# para que "reserva" no sea capturado como un id_usuario.
@app.get("/historial/reserva/{id_reserva}", response_model=DetalleReservaResponse)
async def detalle_reserva(id_reserva: str):
    try:
        reserva_raw = await services.get_reserva(id_reserva)
    except ExternalServiceError as exc:
        _handle_external(exc)

    id_huesped = str(reserva_raw.get("id_huesped", ""))
    try:
        id_prop = int(reserva_raw.get("id_propiedad"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=502, detail="La reserva no tiene un id_propiedad valido")

    try:
        huesped_raw, prop_raw = await asyncio.gather(
            services.get_usuario(id_huesped),
            _fetch_propiedades({id_prop}),
        )
    except ExternalServiceError as exc:
        _handle_external(exc)

    return DetalleReservaResponse(
        reserva=ReservaDetalle(
            id_reserva=_reserva_id(reserva_raw),
            id_huesped=id_huesped,
            id_propiedad=id_prop,
            fecha_checkin=str(reserva_raw.get("fecha_checkin"))[:10] if reserva_raw.get("fecha_checkin") else None,
            fecha_checkout=str(reserva_raw.get("fecha_checkout"))[:10] if reserva_raw.get("fecha_checkout") else None,
            precio_total=reserva_raw.get("precio_total"),
            estado_reserva=reserva_raw.get("estado_reserva"),
            fecha_creacion=str(reserva_raw.get("fecha_creacion")) if reserva_raw.get("fecha_creacion") else None,
        ),
        huesped=_build_huesped(huesped_raw),
        propiedad=_build_propiedad(id_prop, prop_raw.get(id_prop)),
    )


@app.get("/historial/{id_usuario}", response_model=HistorialResponse)
async def historial_completo(id_usuario: str):
    if not id_usuario or not id_usuario.strip():
        raise HTTPException(status_code=400, detail="El id_usuario es obligatorio")
    try:
        huesped_raw, reservas_raw = await asyncio.gather(
            services.get_usuario(id_usuario),
            services.get_reservas_huesped(id_usuario),
        )
    except ExternalServiceError as exc:
        _handle_external(exc)

    huesped = _build_huesped(huesped_raw)
    if not reservas_raw:
        return HistorialResponse(huesped=huesped, stats=Stats(), viajes=[])

    ids_prop = set()
    for r in reservas_raw:
        try:
            ids_prop.add(int(r.get("id_propiedad")))
        except (TypeError, ValueError):
            continue
    props = await _fetch_propiedades(ids_prop)

    viajes = []
    for r in reservas_raw:
        try:
            pid = int(r.get("id_propiedad"))
        except (TypeError, ValueError):
            continue
        viajes.append(_enrich_reserva(r, props.get(pid)))
    viajes.sort(key=lambda v: v.fecha_checkin or "", reverse=True)

    return HistorialResponse(huesped=huesped, stats=_build_stats(viajes), viajes=viajes)


@app.get("/historial/{id_usuario}/resumen", response_model=ResumenResponse)
async def historial_resumen(id_usuario: str):
    if not id_usuario or not id_usuario.strip():
        raise HTTPException(status_code=400, detail="El id_usuario es obligatorio")
    try:
        huesped_raw, reservas_raw = await asyncio.gather(
            services.get_usuario(id_usuario),
            services.get_reservas_huesped(id_usuario),
        )
    except ExternalServiceError as exc:
        _handle_external(exc)

    huesped = _build_huesped(huesped_raw)
    if not reservas_raw:
        stats = Stats()
        return ResumenResponse(huesped=huesped, stats=stats, proximo_viaje=None)

    # Resumen sin MS2: viajes con propiedad=None, solo fechas para stats/proximo.
    viajes = [_enrich_reserva(r, None) for r in reservas_raw if r.get("id_propiedad") is not None]
    viajes.sort(key=lambda v: v.fecha_checkin or "", reverse=True)
    stats = _build_stats(viajes)
    return ResumenResponse(huesped=huesped, stats=stats, proximo_viaje=stats.proximo_viaje)
