# Properties Microservice

Microservicio de **Catálogo de Propiedades** (Microservicio 2) para la Plataforma de Alquiler de Alojamientos.

- **Tecnología:** Java 17 (Spring Boot), MySQL, Spring Data JPA, Docker
- **Puerto de la API:** `8081`
- **Puerto de la BD:** `3307`
- **Documentación interactiva:** `http://localhost:8081/swagger-ui.html`

---

## Estructura del proyecto

```
properties_microservice/
├── src/main/java/com/proyectocloud/properties/
│   ├── PropertiesApplication.java   # Punto de entrada (Spring Boot)
│   ├── entity/                      # Property, Location (equivalente a models.py)
│   ├── dto/                         # PropertyDtos: request/response (equivalente a schemas.py)
│   ├── repository/                  # PropertyRepository (equivalente a crud.py)
│   └── controller/                  # PropertyController: rutas + lógica (equivalente a main.py)
├── src/main/resources/application.yml
├── scripts/
│   └── generate_fake_data.py        # Genera 20,000 registros de prueba
├── init.sql                         # Script de inicialización de la BD
├── Dockerfile
├── docker-compose.yml
└── .env.example                     # Copiar como .env y ajustar valores
```

No hay una capa de "service" separada: con un CRUD de este tamaño, el controller habla directo
con el repositorio (mismo criterio que `main.py` + `crud.py` en el microservicio de Usuarios).

---

## Responsabilidad y límites

- Dueño de las tablas `propiedades` y `ubicaciones` (relación 1 a 1).
- `id_anfitrion` es una **referencia lógica** al microservicio de Usuarios (MS1): se guarda como texto,
  nunca se valida contra esa base de datos ni existe una FK física entre microservicios.

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/properties` | Crear propiedad (nace en estado `ACTIVO`) |
| GET | `/properties` | Listar todas las propiedades |
| GET | `/properties/{id}` | Obtener propiedad + ubicación |
| PUT | `/properties/{id}` | Actualizar propiedad (incluye `estado` y ubicación) |
| DELETE | `/properties/{id}` | Borrado lógico (`estado = INACTIVO`) |

## Decisiones de implementación (no exigidas literalmente por la spec)

| Decisión | Elegido | Motivo |
|---|---|---|
| Eliminar propiedad | Lógica (`estado=INACTIVO`), no `DELETE` físico | Si ya hay reservas/reseñas apuntando a esa propiedad en otro MS, no se pierde el histórico |
| `estado` en creación | Lo fija el servidor en `ACTIVO` | Comportamiento razonable por defecto para un anuncio nuevo |
| Relación Property↔Location | 1 a 1, dueña `Location` (FK `id_propiedad`) | La spec define una sola ubicación por propiedad |
| Esquema de BD | `ddl-auto: update` (Hibernate crea/ajusta tablas si `init.sql` no corrió) | Mismo criterio que `models.Base.metadata.create_all()` en Usuarios |

---

## Variables de entorno (`.env` / `.env.example`)

La plantilla versionada es [`./.env.example`](./.env.example). Cópiala como `.env` y ajusta los valores:

```bash
cp .env.example .env   # luego edita .env si necesitas cambiar claves
```

Referencia de `.env.example` (ver archivo para valores completos):

```env
DB_HOST=db_properties
DB_PORT=3306
DB_NAME=properties_db
DB_USER=properties_user
DB_PASSWORD=properties_password
MYSQL_ROOT_PASSWORD=rootpassword
SERVER_PORT=8081
JPA_DDL_AUTO=update
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DB_HOST` | Sí | Host MySQL. En Docker `db_properties` (`docker-compose.yml:5`); en local `localhost` |
| `DB_PORT` | Sí | Puerto MySQL `3306` interno / `3307` mapeado al host (`docker-compose.yml:14`, `application.yml:9`) |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Sí | Nombre/BD/credenciales (`application.yml:9-11`) |
| `MYSQL_ROOT_PASSWORD` | Sí | Clave root para healthcheck `mysqladmin ping` (`docker-compose.yml:19`) |
| `SERVER_PORT` | No (default `8081`) | Puerto Spring Boot (`application.yml:2`) |
| `JPA_DDL_AUTO` | No (default `update`) | `update` crea/ajusta tablas si `init.sql` no corrió |

> Para poblado desde host (`scripts/generate_fake_data.py` fuera de Docker) usa `DB_HOST=localhost` y `DB_PORT=3307` — ver `scripts/.env` y sección de poblar datos.

---

## Requisitos previos

- **Docker** y **Docker Compose** instalados
- **Java 17+** y **Maven** (si se ejecuta sin Docker)

## Ejecución con Docker Compose (recomendado)

```bash
cd properties_microservice
cp .env.example .env      # plantilla -> ver sección Variables de entorno
docker compose up --build
```

- API: `http://localhost:8081` (`SERVER_PORT`)
- MySQL expuesto en el host: `localhost:3307` (`3307:3306` en `docker-compose.yml:14`)

## Poblar datos de prueba (20,000 registros)

### Opción A — Dentro de Docker (recomendado, usa la red interna)

```bash
# Usa el servicio `seed` definido en docker-compose.yml (profile seed)
docker compose --profile seed run --rm seed
# o manualmente con el compose ya levantado:
docker compose up -d
docker compose exec api_properties python scripts/generate_fake_data.py
```

El servicio `seed` reutiliza automáticamente el `.env` raíz (`DB_HOST=db_properties`, `DB_PORT=3306`) — ver `docker-compose.yml:35`.

### Opción B — Desde el host

```bash
cd scripts
pip install -r requirements.txt
# El script lee DB_HOST/DB_PORT del .env del host: MySQL expuesto en localhost:3307
# Crea scripts/.env o exporta variables (ver scripts/.env de ejemplo con DB_HOST=localhost, DB_PORT=3307):
cp ../.env.example .env   # y ajusta DB_HOST=localhost, DB_PORT=3307
# o usa el archivo ya preparado:
cat ../scripts/.env
python generate_fake_data.py
```

Genera `propiedades` con anfitriones aleatorios y su `ubicacion` 1:1 correspondiente (`scripts/generate_fake_data.py`).

## Notas para el despliegue en AWS

- Todo se configura por variables de entorno (`DB_HOST`, `DB_PORT`, etc.), así que en producción
  solo hay que apuntar `DB_HOST` a la MySQL de la 3ra MV privada.
- Swagger queda disponible para documentar la API que se expone vía AWS API Gateway.
