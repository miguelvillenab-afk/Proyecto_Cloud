import os
import httpx
from dotenv import load_dotenv

load_dotenv()

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000").rstrip("/")
RESERVATIONS_SERVICE_URL = os.getenv("RESERVATIONS_SERVICE_URL", "http://localhost:3000").rstrip("/")
PROPERTY_SERVICE_URL = os.getenv("PROPERTY_SERVICE_URL", "http://localhost:8081").rstrip("/")
REQUEST_TIMEOUT_MS = int(os.getenv("REQUEST_TIMEOUT_MS", "5000"))
REQUEST_TIMEOUT_S = REQUEST_TIMEOUT_MS / 1000.0


class ExternalServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _map_httpx_error(exc: Exception, entidad: str) -> ExternalServiceError:
    if isinstance(exc, httpx.HTTPStatusError) and exc.response is not None:
        status = exc.response.status_code
        if status == 404:
            return ExternalServiceError(f"{entidad} no existe", 404)
        if status == 400:
            try:
                detail = exc.response.json().get("detail", exc.response.text)
            except Exception:
                detail = exc.response.text
            return ExternalServiceError(str(detail)[:300], 400)
        return ExternalServiceError(
            f"El servicio externo respondio con un error inesperado ({status})", 502
        )
    return ExternalServiceError(
        f"No fue posible comunicarse con el servicio externo ({entidad})", 503
    )


async def get_usuario(id_usuario: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            resp = await client.get(f"{USER_SERVICE_URL}/usuarios/{id_usuario}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise _map_httpx_error(exc, "El usuario (huesped)") from exc


async def get_reservas_huesped(id_huesped: str) -> list:
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            resp = await client.get(
                f"{RESERVATIONS_SERVICE_URL}/reservas/huesped/{id_huesped}"
            )
            resp.raise_for_status()
            data = resp.json()
            return data if isinstance(data, list) else []
    except httpx.HTTPError as exc:
        raise _map_httpx_error(exc, "Las reservas del huesped") from exc


async def get_reserva(id_reserva: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            resp = await client.get(f"{RESERVATIONS_SERVICE_URL}/reservas/{id_reserva}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise _map_httpx_error(exc, "La reserva") from exc


async def get_propiedad(id_propiedad: int) -> dict:
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
            resp = await client.get(f"{PROPERTY_SERVICE_URL}/properties/{id_propiedad}")
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError as exc:
        raise _map_httpx_error(exc, "La propiedad") from exc
