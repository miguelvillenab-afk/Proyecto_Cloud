# User Microservice

Microservicio de gestión de usuarios (huéspedes y anfitriones) para la Plataforma de Alquiler de Alojamientos.

- **Tecnología:** Python (FastAPI), PostgreSQL, SQLAlchemy, Docker
- **Puerto de la API:** `8000`
- **Puerto de la BD:** `5433`
- **Documentación interactiva:** `http://localhost:8000/docs`

---

## Estructura del proyecto

```
user_microservice/
├── app/
│   ├── __init__.py
│   ├── main.py          # Punto de entrada de la API (FastAPI)
│   ├── database.py      # Configuración de conexión a PostgreSQL
│   ├── models.py        # Modelos SQLAlchemy (Usuario, MetodoPago)
│   ├── schemas.py       # Esquemas Pydantic (request/response)
│   └── crud.py          # Lógica de acceso a datos
├── scripts/
│   └── generate_fake_data.py  # Genera 20,000 registros de prueba
├── init.sql             # Script de inicialización de la BD
├── Dockerfile           # Imagen Docker del microservicio
├── docker-compose.yml   # Orquestación de contenedores
├── requirements.txt     # Dependencias de Python
└── .env                 # Variables de entorno (CREAR MANUALMENTE)
```

---

## Requisitos previos

- **Docker** y **Docker Compose** instalados
- **Python 3.11+** (si se ejecuta sin Docker)

---

## Ejecución con Docker Compose (recomendado)

### 1. Crear el archivo `.env` en la raíz del microservicio

Dentro de la carpeta `user_microservice/`, crea un archivo llamado `.env` con el siguiente contenido:

```env
DATABASE_URL=postgresql://postgres:tu_contraseña@db_users:5432/postgres
```

> **Nota:** Reemplaza `tu_contraseña` con la contraseña que definas para PostgreSQL. El servicio de BD (`db_users`) se resuelve por el nombre del servicio en Docker Compose, por lo que `db_users` es el host correcto dentro de la red Docker.

### 2. Construir y levantar los contenedores

```bash
cd user_microservice
docker-compose up --build
```

Esto hará lo siguiente:

1. **`db_users`** — Levanta PostgreSQL 15 en el puerto local `5433`:
   - Ejecuta automáticamente `init.sql` al arrancar (crea las tablas `Usuarios` y `Metodos_Pago`)
   - Habilita la extensión `uuid-ossp`
   - Persiste datos en el volumen `postgres_data`

2. **`api_users`** — Construye la imagen Docker y levanta la API FastAPI en el puerto `8000`
   - Depende de `db_users`, así que espera a que la BD esté lista antes de iniciar

### 3. Verificar que todo funciona

- **API principal:** `http://localhost:8000`
- **Documentación Swagger:** `http://localhost:8000/docs`
- **Documentación alternativa ReDoc:** `http://localhost:8000/redoc`

### 4. Detener los servicios

```bash
docker-compose down
```

Para eliminar también los datos persistentes:

```bash
docker-compose down -v
```

---

## Ejecución manual (sin Docker)

### 1. Instalar dependencias

```bash
cd user_microservice
pip install -r requirements.txt
```

### 2. Crear la base de datos y tablas

Asegúrate de tener PostgreSQL corriendo localmente en el puerto `5432`, luego ejecuta:

```bash
psql -U postgres -d postgres -f init.sql
```

### 3. Crear el archivo `.env`

En la raíz de `user_microservice/`, crea un archivo `.env`:

```env
DATABASE_URL=postgresql://postgres:tu_contraseña@localhost:5432/postgres
```

### 4. Ejecutar el servidor

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Generar datos de prueba (20,000 registros)

El microservicio incluye un script para poblar la base de datos con datos ficticios de prueba:

### Con Docker Compose:

```bash
# Primero levantar el servicio con docker-compose up -d
docker-compose up -d

# Ejecutar el script dentro del contenedor de la API
docker-compose exec api_users python scripts/generate_fake_data.py
```

### Manualmente:

```bash
# Asegúrate de que la API esté corriendo y la BD esté poblada
python scripts/generate_fake_data.py
```

Esto inserta **20,000 usuarios ficticios** en bloques de 5,000 con nombres, emails y roles aleatorios (HUESPED / ANFITRION).

---

## Endpoints de la API

### `POST /usuarios/`
Crea un nuevo usuario. Si el email ya existe, retorna `400`.

**Body:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "password": "contraseña123",
  "rol": "HUESPED"
}
```

> El rol debe ser `HUESPED` o `ANFITRION`. La contraseña se encripta automáticamente con bcrypt.

**Respuesta (201):**
```json
{
  "id_usuario": "a1b2c3d4-...",
  "nombre": "Juan Pérez",
  "email": "juan@email.com",
  "rol": "HUESPED",
  "fecha_registro": "2025-01-15T10:30:00",
  "metodos_pago": []
}
```

### `GET /usuarios/{usuario_id}`
Obtiene los datos de un usuario por su ID (UUID). Retorna `404` si no existe.

### `POST /usuarios/{usuario_id}/metodos-pago/`
Añade un método de pago asociado a un usuario existente.

**Body:**
```json
{
  "tipo_tarjeta": "Visa",
  "ultimos_cuatro": "1234"
}
```

**Respuesta (201):**
```json
{
  "id_metodo": 1,
  "id_usuario": "a1b2c3d4-...",
  "tipo_tarjeta": "Visa",
  "ultimos_cuatro": "1234"
}
```

---

## Modelos de datos

### `Usuarios`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_usuario` | UUID | Clave primaria, generado automáticamente |
| `nombre` | VARCHAR(100) | Nombre completo del usuario |
| `email` | VARCHAR(150) | Email único e indexado |
| `password_hash` | VARCHAR(255) | Contraseña encriptada con bcrypt |
| `rol` | VARCHAR(20) | `HUESPED` o `ANFITRION` |
| `fecha_registro` | TIMESTAMP | Fecha de registro automática |

### `Metodos_Pago`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_metodo` | SERIAL | Clave primaria |
| `id_usuario` | UUID | FK a `Usuarios.id_usuario`, eliminación en cascada |
| `tipo_tarjeta` | VARCHAR(50) | Tipo de tarjeta (Visa, Mastercard, etc.) |
| `ultimos_cuatro` | VARCHAR(4) | Últimos 4 dígitos de la tarjeta |

---

## Dependencias de Python

| Paquete | Versión | Uso |
|---------|---------|-----|
| `fastapi` | 0.103.1 | Framework de la API |
| `uvicorn` | 0.23.2 | Servidor ASGI |
| `sqlalchemy` | 2.0.21 | ORM para PostgreSQL |
| `psycopg2-binary` | 2.9.8 | Driver PostgreSQL |
| `passlib[bcrypt]` | 1.7.4 | Encriptación de contraseñas |
| `faker` | 19.6.1 | Generación de datos ficticios |
| `python-dotenv` | 1.0.0 | Carga de variables de entorno |
| `email-validator` | 2.0.0 | Validación de emails |

---

## Notas importantes

- El puerto local para PostgreSQL es el **`5433`** (mapeado desde `5432` dentro del contenedor para evitar conflictos con otras instalaciones locales de PostgreSQL).
- Las contraseñas **nunca se almacenan en texto plano**; se encriptan con bcrypt antes de guardar en BD.
- Si ejecutas `docker-compose up` sin el archivo `.env`, el servicio fallará al no poder conectar a la base de datos.
- El script `init.sql` se ejecuta automáticamente solo en la **primera inicialización** del volumen de PostgreSQL. Si el volumen ya existe, no se volverá a ejecutar.
