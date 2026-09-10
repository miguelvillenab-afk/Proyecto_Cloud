# User Microservice — Gestión de Usuarios, Auth y Pagos

Microservicio 1 de la Plataforma de Alquiler de Alojamientos. Gestiona **registro y consulta de usuarios** (HUESPED / ANFITRION), **autenticación con JWT** y **métodos de pago** asociados.

- **Stack:** Python 3.11 · FastAPI 0.103.1 · SQLAlchemy 2.0.21 · PostgreSQL 15 · `psycopg2-binary` · `passlib[bcrypt]` · `PyJWT` · Docker Compose
- **API:** `http://localhost:8000` → Swagger UI en `http://localhost:8000/docs` · ReDoc en `http://localhost:8000/redoc`
- **BD:** PostgreSQL 15, host local `localhost:5433` mapeado al `5432` del contenedor

---

## 1. Estructura del proyecto

```
user_microservice/
├── app/
│   ├── __init__.py      # Marca app/ como paquete Python
│   ├── main.py          # App FastAPI + endpoints (/usuarios/, /login/)
│   ├── database.py      # Engine SQLAlchemy, SessionLocal, get_db (lee DATABASE_URL del .env)
│   ├── models.py        # Modelos ORM: Usuario (usuarios) <-> MetodoPago (metodos_pago)
│   ├── schemas.py       # Esquemas Pydantic: UsuarioCreate/Response, MetodoPago*, UsuarioLogin
│   └── crud.py          # Acceso a datos + bcrypt + authenticate_user + create_access_token (JWT)
├── scripts/
│   └── generate_fake_data.py  # Carga masiva de 20,000 usuarios con Faker (batches de 5,000)
├── init.sql             # DDL inicial (extensión uuid-ossp + tablas Usuarios y Metodos_Pago)
├── Dockerfile           # Imagen python:3.11-slim + uvicorn app.main:app --port 8000
├── docker-compose.yml   # Servicios db_users (postgres:15) y api_users (FastAPI)
├── requirements.txt     # Dependencias pinneadas
├── .env.example         # Plantilla versionada (copiar como .env)
└── .env                 # NO versionado — crear con: cp .env.example .env (ver sección 2)
```

### Archivos clave y qué hacen

| Archivo | Responsabilidad |
|---------|-----------------|
| `app/main.py` | Define `FastAPI(title="API de Gestión de Usuarios (Microservicio 1)")`. Hace `Base.metadata.create_all(bind=engine)` como fallback si `init.sql` no corrió. Expone 4 endpoints (ver sección 5). |
| `app/database.py` | Carga `.env` con `python-dotenv`, crea `engine = create_engine(DATABASE_URL)` y expone `get_db()` como dependencia de FastAPI. **Falla al arrancar si `DATABASE_URL` no está definida.** |
| `app/models.py` | `Usuario.__tablename__ = "usuarios"` (UUID PK `default=uuid.uuid4`, email único indexado, `password_hash`, `rol`, `fecha_registro server_default=now()`) + relación `metodos_pago` con `cascade="all, delete-orphan"`. `MetodoPago.__tablename__ = "metodos_pago"` (SERIAL PK, FK a `usuarios.id_usuario ON DELETE CASCADE`). |
| `app/schemas.py` | Validación con Pydantic: `email: EmailStr` (requiere `email-validator`), `UsuarioCreate` exige `password` en claro (se hashea en `crud`), `UsuarioResponse` incluye `metodos_pago: List[MetodoPagoResponse]`, `UsuarioLogin(email, password)`. |
| `app/crud.py` | `pwd_context = CryptContext(schemes=["bcrypt"])` para hash/verify. `create_user` hashea antes de guardar. `authenticate_user` retorna `False` si email/clave fallan. `create_access_token` firma JWT HS256 con `exp = utcnow + JWT_EXPIRATION_MINUTES`. |
| `scripts/generate_fake_data.py` | Inserta 20,000 `Usuario` con `Faker` (`name`, `unique.email`, `sha256()` como hash simulado por velocidad, rol aleatorio). Usa `bulk_save_objects` en bloques de 5,000. **Ojo:** estos registros NO sirven para `/login/` porque el hash no es bcrypt real. |
| `init.sql` | Crea extensión `uuid-ossp` y tablas `Usuarios` / `Metodos_Pago` (nombres con mayúscula). Se monta en `/docker-entrypoint-initdb.d/` y **solo corre en la primera inicialización del volumen**. Ver nota en sección 6. |

---

## 2. Variables de entorno (`.env` / `.env.example`)

La plantilla versionada es [`./.env.example`](./.env.example). Cópiala como `.env` y ajusta los valores:

```bash
cp .env.example .env   # luego edita .env si necesitas cambiar claves
```

Contenido de referencia de `.env.example` (ver archivo para valores por defecto):

```env
# Conexión que usa la API (dentro de Docker el host es el nombre del servicio)
DATABASE_URL=postgresql://admin:secretpassword@db_users:5432/users_db

# Variables que consume la imagen postgres:15 (mismo usuario/clave que arriba)
POSTGRES_USER=admin
POSTGRES_PASSWORD=secretpassword
POSTGRES_DB=users_db

# Auth JWT (usadas en app/crud.py::create_access_token, con defaults si se omiten)
JWT_SECRET_KEY=cambia_esta_clave_en_produccion_usar_un_secreto_largo_y_aleatorio
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

| Variable | Obligatoria | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | URL SQLAlchemy que usa FastAPI (`app/database.py:12`). Dentro de Docker `host=db_users:5432`; en local `localhost:5433`. |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Sí | Credenciales que consume `postgres:15` (`docker-compose.yml:4`). Deben coincidir con `DATABASE_URL`. |
| `JWT_SECRET_KEY` | Sí (prod) | Clave HS256 para `crud.create_access_token`. Usa un secreto largo/aleatorio en producción. |
| `JWT_ALGORITHM` | No (default `HS256`) | Algoritmo de firma. |
| `JWT_EXPIRATION_MINUTES` | No (default `60`) | Expiración del token. |

> Sin `.env` el contenedor `api_users` falla (`DATABASE_URL=None` → `create_engine(None)` levanta excepción) y `db_users` arranca con clave aleatoria. Para ejecución manual sin Docker cambia el host a `localhost:5432` (o `localhost:5433` si usas el contenedor de BD). Ver `DATABASE_URL` comentado al final de `.env.example`.

---

## 3. Requisitos previos

- Docker + Docker Compose (flujo recomendado)
- Python 3.11+ + PostgreSQL local (solo para flujo manual)
- Puertos libres: `8000` (API) y `5433` (BD)

---

## 4. Ejecución

### Opción A — Docker Compose (recomendado)

```bash
cd user_microservice

# 1. Crear el .env desde la plantilla (ver sección 2)
cp .env.example .env   # ajusta claves si es necesario

# 2. Construir y levantar (db_users + api_users)
docker compose up --build
# o en versiones antiguas: docker-compose up --build

# 3. Verificar
# Swagger: http://localhost:8000/docs
# ReDoc:   http://localhost:8000/redoc
```

Qué levanta:

1. **`db_users`** — `postgres:15` en `localhost:5433→5432`. Ejecuta `init.sql` solo la primera vez. Datos persistidos en volumen `postgres_data`.
2. **`api_users`** — FastAPI + Uvicorn en `:8000`, con `depends_on: db_users`.

Detener:

```bash
docker compose down        # conserva datos
docker compose down -v     # borra también el volumen postgres_data (init.sql volverá a correr)
```

### Opción B — Manual (sin Docker)

```bash
cd user_microservice
pip install -r requirements.txt

# 1. Crear tablas (PostgreSQL local en :5432)
psql -U postgres -d postgres -f init.sql

# 2. Crear .env desde plantilla y apuntar a localhost (ver sección 2 / .env.example)
cp .env.example .env
# Edita DATABASE_URL a: postgresql://admin:secretpassword@localhost:5433/users_db

# 3. Arrancar API
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 5. Endpoints de la API

> No existe `GET /` raíz. Usa `/docs` para probar interactivamente.

### `POST /usuarios/` — Registrar usuario

Crea usuario con password hasheada en bcrypt. `400` si el email ya existe.

```bash
curl -X POST http://localhost:8000/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Juan Pérez","email":"juan@email.com","password":"contraseña123","rol":"HUESPED"}'
```

Respuesta `200 OK` (nótese: sin `status_code=201` explícito en `main.py`, FastAPI retorna 200 por defecto):

```json
{
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "rol": "HUESPED",
  "id_usuario": "a1b2c3d4-...",
  "fecha_registro": "2025-01-15T10:30:00",
  "metodos_pago": []
}
```

Validaciones: `email` con formato válido (`EmailStr`), `rol` libre a nivel Pydantic pero restringido a `HUESPED`/`ANFITRION` por el `CHECK` de `init.sql` (a nivel ORM no hay validación — un rol inválido falla en BD si la tabla vino de `init.sql`, pero pasa si la tabla fue creada por `create_all`).

### `GET /usuarios/{usuario_id}` — Obtener usuario por UUID

```bash
curl http://localhost:8000/usuarios/a1b2c3d4-...
```

Retorna el mismo esquema `UsuarioResponse` (con `metodos_pago` anidados). `404 {"detail":"Usuario no encontrado"}` si no existe o el UUID es inválido.

### `POST /usuarios/{usuario_id}/metodos-pago/` — Añadir método de pago

Valida que el usuario exista primero (`404` si no).

```bash
curl -X POST http://localhost:8000/usuarios/a1b2c3d4-.../metodos-pago/ \
  -H "Content-Type: application/json" \
  -d '{"tipo_tarjeta":"Visa","ultimos_cuatro":"1234"}'
```

Respuesta:

```json
{
  "tipo_tarjeta": "Visa",
  "ultimos_cuatro": "1234",
  "id_metodo": 1,
  "id_usuario": "a1b2c3d4-..."
}
```

### `POST /login/` — Autenticarse y obtener JWT

Verifica email + bcrypt y retorna un Bearer token firmado con `JWT_SECRET_KEY`.

```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"juan@email.com","password":"contraseña123"}'
```

Respuesta:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "usuario_id": "a1b2c3d4-...",
  "rol": "HUESPED"
}
```

- Payload del token: `{"sub": "<id_usuario>", "rol": "<rol>", "exp": "<utcnow + JWT_EXPIRATION_MINUTES>"}`.
- Error: `401 {"detail":"Correo o contraseña incorrectos"}` si falla.
- **Ningún endpoint actual valida el token** — el JWT se emite pero no hay dependencia de autenticación en las demás rutas (pendiente proteger rutas si se requiere).

---

## 6. Modelos de datos

### `usuarios` (ORM) / `Usuarios` (init.sql)

| Campo | Tipo | Notas |
|-------|------|-------|
| `id_usuario` | UUID PK | `default=uuid.uuid4` (ORM) / `uuid_generate_v4()` (SQL) |
| `nombre` | VARCHAR(100) NOT NULL | |
| `email` | VARCHAR(150) UNIQUE, indexado, NOT NULL | Validado como `EmailStr` en API |
| `password_hash` | VARCHAR(255) NOT NULL | bcrypt vía passlib. **Nunca se expone en respuestas** |
| `rol` | VARCHAR(20) NOT NULL | `CHECK (rol IN ('HUESPED','ANFITRION'))` solo en `init.sql` |
| `fecha_registro` | TIMESTAMP, default `now()` | |

### `metodos_pago` (ORM) / `Metodos_Pago` (init.sql)

| Campo | Tipo | Notas |
|-------|------|-------|
| `id_metodo` | SERIAL PK | |
| `id_usuario` | UUID NOT NULL, FK → `usuarios.id_usuario ON DELETE CASCADE` | Borrar usuario elimina sus pagos (ORM + BD) |
| `tipo_tarjeta` | VARCHAR(50) NOT NULL | Ej. Visa, Mastercard |
| `ultimos_cuatro` | VARCHAR(4) NOT NULL | Sin validación de longitud exacta en Pydantic |

> **Inconsistencia de nombres a tener en cuenta:** `init.sql` crea `Usuarios`/`Metodos_Pago` (con mayúsculas, case-sensitive entre comillas implícitas → Postgres las guarda en minúsculas salvo quoting, por lo que en la práctica coinciden), mientras `models.py` declara `usuarios`/`metodos_pago` y además ejecuta `create_all()` al importar `main.py`. Si el volumen ya existe con un esquema previo, `init.sql` no se re-ejecuta y manda el esquema creado por SQLAlchemy. Para un estado limpio: `docker compose down -v && docker compose up --build`.

---

## 7. Datos de prueba (20,000 registros)

```bash
# Con la API/BD ya levantadas:
docker compose up -d
docker compose exec api_users python scripts/generate_fake_data.py

# O en local:
python scripts/generate_fake_data.py
```

Inserta 20,000 usuarios en 4 lotes de 5,000 (`bulk_save_objects` + `commit` por lote). Usa hash `sha256()` simulado por velocidad — **esos usuarios NO pueden usar `/login/`** (espera bcrypt). Para probar login, crea usuarios vía `POST /usuarios/`.

---

## 8. Dependencias (`requirements.txt`)

| Paquete | Versión | Uso |
|---------|---------|-----|
| `fastapi` | 0.103.1 | Framework API + Swagger `/docs` |
| `uvicorn` | 0.23.2 | Servidor ASGI (`app.main:app`) |
| `sqlalchemy` | 2.0.21 | ORM + engine/sesiones |
| `psycopg2-binary` | 2.9.8 | Driver PostgreSQL |
| `passlib[bcrypt]` | 1.7.4 | Hash/verify de contraseñas |
| `PyJWT` | 2.8.0 | Firma y emisión de tokens en `crud.create_access_token` |
| `faker` | 19.6.1 | Generación de datos masivos |
| `python-dotenv` | 1.0.0 | Carga `.env` en `database.py` y script de datos |
| `email-validator` | 2.0.0.post2 | Validación de `EmailStr` en schemas |

---

## 9. Troubleshooting

| Síntoma | Causa probable / solución |
|---------|---------------------------|
| `api_users` crashea con `TypeError` en `create_engine` | Falta `DATABASE_URL` en `.env`. Créalo según sección 2. |
| `POST /usuarios` falla con error de CHECK en `rol` | Usa exactamente `HUESPED` o `ANFITRION` en mayúsculas. |
| `init.sql` no parece aplicarse | Solo corre con volumen nuevo: `docker compose down -v && docker compose up --build`. |
| Puerto `5433` ocupado | Otro Postgres local. Cambia el mapeo en `docker-compose.yml` o detén el servicio local. |
| `/login/` retorna 401 con datos del script fake | Esperado: esos hashes son `sha256()` simulados, no bcrypt. Registra el usuario por API. |
| Token expirado / firma inválida en otros servicios | Verifica que `JWT_SECRET_KEY` y `JWT_ALGORITHM` sean iguales en todos los microservicios consumidores. |
