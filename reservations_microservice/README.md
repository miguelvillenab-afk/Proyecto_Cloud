# Reservations Microservice

Microservicio de gestión de reservas y reseñas para la Plataforma de Alquiler de Alojamientos. Valida al huésped y a la propiedad consumiendo, respectivamente, las APIs del `user_microservice` (MS1) y del `properties_microservice` (MS2) antes de confirmar una reserva.

- **Tecnología:** Node.js (Express), MongoDB, Mongoose, Docker
- **Puerto de la API:** `3000`
- **Puerto de la BD:** `27018`
- **Documentación de referencia:** ver sección [Endpoints de la API](#endpoints-de-la-api)

> **Nota de diseño:** se usó Express (en vez de NestJS) para mantener el mismo enfoque directo y minimalista de funciones que usa `user_microservice` (FastAPI), en vez de la estructura más pesada basada en clases/decoradores de NestJS.

---

## Estructura del proyecto

```
reservations_microservice/
├── app/
│   ├── main.js            # Definición de la app Express y montaje de rutas
│   ├── database.js        # Configuración de conexión a MongoDB
│   ├── models.js          # Esquemas Mongoose (Reserva, Resena)
│   ├── schemas.js         # Validación de entrada con Joi (request bodies)
│   ├── services.js        # Cliente HTTP hacia MS1 (usuarios) y MS2 (propiedades)
│   ├── crud.js             # Lógica de acceso a datos (MongoDB)
│   └── routes/
│       ├── reservas.routes.js
│       └── resenas.routes.js
├── scripts/
│   └── generate_fake_data.js  # Genera 20,000 registros de prueba
├── server.js               # Punto de entrada (conecta a Mongo y levanta Express)
├── package.json             # Dependencias de Node.js
├── Dockerfile                # Imagen Docker del microservicio
├── docker-compose.yml        # Orquestación de contenedores
├── .env.example               # Plantilla de variables de entorno
└── .env                       # Variables de entorno (CREAR MANUALMENTE)
```

---

## Requisitos previos

- **Docker** y **Docker Compose** instalados
- **Node.js 18+** (si se ejecuta sin Docker)
- El `user_microservice` (MS1) y el `properties_microservice` (MS2) deben estar accesibles en red para que la validación de reservas funcione.

---

## Variables de entorno

Copia `.env.example` a `.env` dentro de `reservations_microservice/` y ajusta los valores:

```env
PORT=3000
MONGODB_URI=mongodb://db_reservations:27017/reservations_db
USER_SERVICE_URL=http://api_users:8000
PROPERTY_SERVICE_URL=http://api_properties:8080
```

> **Nota:** `db_reservations` es el nombre del servicio Mongo dentro de la red de Docker Compose de este microservicio. `api_users` y `api_properties` deben ser resolubles desde este contenedor (por ejemplo, conectando ambos `docker-compose.yml` a una misma red externa de Docker, o usando la IP/host real de cada servicio en despliegue).

---

## Ejecución con Docker Compose (recomendado)

```bash
cd reservations_microservice
docker-compose up --build
```

Esto hará lo siguiente:

1. **`db_reservations`** — Levanta MongoDB 6 en el puerto local `27018`, persistiendo datos en el volumen `mongo_data`.
2. **`api_reservations`** — Construye la imagen Docker y levanta la API Express en el puerto `3000`. Depende de `db_reservations`.

### Verificar que todo funciona

- **API principal:** `http://localhost:3000`

### Detener los servicios

```bash
docker-compose down
```

Para eliminar también los datos persistentes:

```bash
docker-compose down -v
```

---

## Ejecución manual (sin Docker)

```bash
cd reservations_microservice
npm install
# Asegúrate de tener MongoDB corriendo localmente y el .env apuntando a él
npm start
```

Para desarrollo con recarga automática:

```bash
npm run dev
```

---

## Generar datos de prueba (20,000 registros)

### Con Docker Compose:

```bash
docker-compose up -d
docker-compose exec api_reservations npm run seed
```

### Manualmente:

```bash
npm run seed
```

Esto inserta **20,000 reservas ficticias** en bloques de 5,000, con `id_huesped` e `id_propiedad` simulados (no se validan contra MS1/MS2 durante la carga masiva, igual que el script equivalente del MS1 no valida nada al poblar `Usuarios`).

---

## Integración con MS1 y MS2

Al crear una reserva (`POST /reservas/`), el microservicio ejecuta, en orden:

1. **Validación del huésped (MS1):** `GET {USER_SERVICE_URL}/usuarios/{id_huesped}`. Si responde `404`, la reserva se rechaza con `404` y el detalle "El usuario (huésped) no existe".
2. **Validación de la propiedad (MS2):** `GET {PROPERTY_SERVICE_URL}/propiedades/{id_propiedad}`. Se espera un JSON con al menos el campo `precio_noche`. Si responde `404`, la reserva se rechaza con `404` y el detalle "La propiedad no existe".
3. **Cálculo del valor de la reserva:** `precio_total = noches_solicitadas * precio_noche`, redondeado a 2 decimales.
4. **Errores de comunicación:** si el MS1 o el MS2 no responden (timeout, servicio caído), se devuelve `503`. Si responden con un código HTTP inesperado distinto de 404, se devuelve `502`.

> **Supuesto documentado:** como el `properties_microservice` (MS2, Java/Spring Boot) aún no forma parte de este repositorio, se asumió el contrato `GET /propiedades/{id}` devolviendo `precio_noche` según lo descrito en las especificaciones del proyecto. Si el MS2 real usa otro nombre de campo (p. ej. `precioNoche`) o ruta distinta, ajustar `app/services.js` (la función ya intenta ambos nombres de campo) y la variable `PROPERTY_SERVICE_URL`.

---

## Endpoints de la API

### `POST /reservas/`
Crea una nueva reserva, validando huésped y propiedad contra MS1 y MS2.

**Body:**
```json
{
  "id_huesped": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "id_propiedad": 105,
  "fecha_checkin": "2026-10-15",
  "fecha_checkout": "2026-10-20"
}
```

**Respuesta (201):**
```json
{
  "_id": "651f1c2e8f1b2a0012345678",
  "id_huesped": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "id_propiedad": 105,
  "fecha_checkin": "2026-10-15T00:00:00.000Z",
  "fecha_checkout": "2026-10-20T00:00:00.000Z",
  "precio_total": 450.50,
  "estado_reserva": "CONFIRMADA",
  "fecha_creacion": "2026-09-09T10:00:00.000Z"
}
```

**Errores posibles:** `400` (validación de body o fechas), `404` (usuario o propiedad inexistente), `502`/`503` (falla de comunicación con MS1/MS2).

### `GET /reservas/:id`
Obtiene una reserva por su `ObjectId`. Retorna `404` si no existe.

### `GET /reservas/huesped/:id_huesped`
Lista todas las reservas de un huésped.

### `PATCH /reservas/:id/estado`
Actualiza el estado de una reserva.

**Body:**
```json
{ "estado_reserva": "CANCELADA" }
```

### `POST /resenas/`
Crea una reseña asociada a una reserva existente. Retorna `404` si la reserva no existe.

**Body:**
```json
{
  "id_reserva": "651f1c2e8f1b2a0012345678",
  "calificacion": 5,
  "comentario": "Excelente lugar, muy limpio."
}
```

**Respuesta (201):**
```json
{
  "_id": "651f1c9a8f1b2a0012345679",
  "id_reserva": "651f1c2e8f1b2a0012345678",
  "id_propiedad": 105,
  "id_huesped": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "calificacion": 5,
  "comentario": "Excelente lugar, muy limpio.",
  "fecha_creacion": "2026-09-09T10:05:00.000Z"
}
```

### `GET /resenas/propiedad/:id_propiedad`
Lista las reseñas de una propiedad.

---

## Modelos de datos

### `Reservas` (colección MongoDB)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_id` | ObjectId | Identificador generado por MongoDB |
| `id_huesped` | String (UUID) | Referencia lógica a `Usuarios.id_usuario` del MS1 |
| `id_propiedad` | Number | Referencia lógica a `Propiedades.id_propiedad` del MS2 |
| `fecha_checkin` | Date | Fecha de entrada |
| `fecha_checkout` | Date | Fecha de salida (debe ser posterior al checkin) |
| `precio_total` | Number | Calculado a partir de `precio_noche` del MS2 |
| `estado_reserva` | String | `PENDIENTE`, `CONFIRMADA`, `CANCELADA` o `COMPLETADA` |
| `fecha_creacion` | Date | Timestamp automático |

### `Resenas` (colección MongoDB)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `_id` | ObjectId | Identificador generado por MongoDB |
| `id_reserva` | ObjectId | FK lógica a `Reservas._id` |
| `id_propiedad` | Number | Derivado de la reserva asociada |
| `id_huesped` | String (UUID) | Derivado de la reserva asociada |
| `calificacion` | Number | Entero entre 1 y 5 |
| `comentario` | String | Comentario libre (máx. 500 caracteres) |
| `fecha_creacion` | Date | Timestamp automático |

---

## Dependencias de Node.js

| Paquete | Uso |
|---------|-----|
| `express` | Framework HTTP de la API |
| `mongoose` | ODM para MongoDB |
| `axios` | Cliente HTTP para consumir MS1 y MS2 |
| `joi` | Validación de los cuerpos de las peticiones |
| `dotenv` | Carga de variables de entorno |
| `@faker-js/faker` | Generación de datos ficticios para el script de carga masiva |
| `nodemon` (dev) | Recarga automática en desarrollo |

---

## Notas importantes

- El puerto local para MongoDB es el **`27018`** (mapeado desde `27017` dentro del contenedor, para evitar conflictos con instalaciones locales de MongoDB), siguiendo el mismo criterio que `user_microservice` usa con `5433` para PostgreSQL.
- Si ejecutas `docker-compose up` sin el archivo `.env`, el servicio fallará al no poder resolver `MONGODB_URI`, `USER_SERVICE_URL` ni `PROPERTY_SERVICE_URL`.
- Para que la validación contra MS1/MS2 funcione en Docker, los tres microservicios deben poder resolverse entre sí por nombre de red (por ejemplo, conectando sus respectivos `docker-compose.yml` a una red Docker externa compartida) o mediante las IPs/hosts reales del entorno de despliegue en AWS.
- El precio de la reserva **nunca se recibe del cliente**: siempre se recalcula en el servidor a partir del `precio_noche` que reporta el MS2, para evitar manipulación del monto desde el frontend.
