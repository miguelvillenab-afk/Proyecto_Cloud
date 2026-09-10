# MS4 - Historial de Viajes del Huésped

Agregador **sin base de datos propia**. Expone la "Historia del Viajero" consultando MS1, MS3 y MS2.

*Tecnología:* Python 3.11 · FastAPI 0.103.1 · httpx 0.25.2 · Uvicorn

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Health check `{status: ok}` |
| `GET` | `/historial/{id_usuario}` | Perfil + stats + timeline enriquecida |
| `GET` | `/historial/{id_usuario}/resumen` | Solo perfil + stats + próximo viaje (sin MS2, liviano) |
| `GET` | `/historial/reserva/{id_reserva}` | Detalle rico de 1 reserva (reserva + huésped + propiedad) |
| `GET` | `/docs` | Swagger UI |

## Dependencias externas

* MS1 `GET /usuarios/{id}` → perfil del huésped.
* MS3 `GET /reservas/huesped/{id}` → todas las reservas del huésped. `GET /reservas/{id}` → una reserva.
* MS2 `GET /properties/{id}` → `titulo` + `ubicacion{ciudad,pais,direccion}` (foto omitida por spec).

Errores propagados: MS1/MS3 404 → 404, otro HTTP → 502, timeout/caída → 503. Propiedad 404 → `propiedad: null` sin tumbar el historial.

## Variables de entorno (`.env` ← `.env.example`)

| Variable | Ejemplo |
|---|---|
| `PORT` | `8082` |
| `USER_SERVICE_URL` | `http://host.docker.internal:8000` |
| `RESERVATIONS_SERVICE_URL` | `http://host.docker.internal:3000` |
| `PROPERTY_SERVICE_URL` | `http://host.docker.internal:8081` |
| `REQUEST_TIMEOUT_MS` | `5000` |

## Ejecución con Docker (forma oficial)

> Este microservicio **solo se levanta con Docker** (no requiere instalación local de Python ni BD propia).
> Pre-requisito: MS1 (8000), MS3 (3000) y MS2 (8081) levantados primero para datos reales.

```bash
cd history_microservice
cp .env.example .env   # solo la primera vez
docker compose up --build -d
docker compose ps
curl http://localhost:8082/health   # -> {"status":"ok"}
curl http://localhost:8082/          # info del servicio
# Swagger: http://localhost:8082/docs
```

Comandos útiles:

```bash
docker compose logs -f api_history  # ver logs
docker compose down                 # detener
docker compose up --build -d        # reconstruir tras cambios
```

Notas:
* Puerto API `8082:8082` (ver `docker-compose.yml`). Sin puertos de BD porque no tiene BD.
* `extra_hosts: host.docker.internal:host-gateway` permite que el contenedor alcance a MS1/MS2/MS3 en `localhost:8000/8081/3000` del host. Si unes los compose en una misma red, usa la OPCIÓN B del `.env.example` (`http://api_users:8000`, etc.).
* El contenedor lee variables desde `.env` (`env_file: .env`).


## Ejecución manual

```bash
cd history_microservice && cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8082
```

> Requiere MS1 (8000), MS3 (3000) y MS2 (8081) levantados para datos reales.

## Ejemplos

```bash
curl http://localhost:8082/health
curl http://localhost:8082/historial/<uuid-huesped>
curl http://localhost:8082/historial/<uuid-huesped>/resumen
curl http://localhost:8082/historial/reserva/<ObjectId-mongo>
```
