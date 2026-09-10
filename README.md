# Proyecto Cloud Computing: Plataforma de Alquiler de Alojamientos

Plataforma integral de alquiler de alojamientos donde los usuarios interactúan como **Anfitriones** (para publicar propiedades) o **Huéspedes** (para buscar y reservar). El sistema permite gestionar perfiles, publicar anuncios, realizar reservas y analizar el rendimiento del negocio mediante métricas avanzadas.

---

## 📋 Estado actual del repositorio

| Microservicio | Estado | Stack | Puerto API → Host | Puerto BD → Host | README | `.env.example` |
|---|---|---|---|---|---|---|
| **01 - Gestión de Usuarios** `user_microservice` | ✅ Implementado | Python 3.11 · FastAPI 0.103.1 · SQLAlchemy 2.0 · PostgreSQL 15 | `8000` → `localhost:8000` (`docker-compose.yml:21`) | `5432` → `localhost:5433` | [`user_microservice/README.md`](./user_microservice/README.md) | [`user_microservice/.env.example`](./user_microservice/.env.example) |
| **02 - Catálogo de Propiedades** `properties_microservice` | ✅ Implementado | Java 17 · Spring Boot · MySQL 8.0 · Spring Data JPA | `8081` → `localhost:8081` (`application.yml:2`, `docker-compose.yml:28`) | `3306` → `localhost:3307` | [`properties_microservice/README.md`](./properties_microservice/README.md) | [`properties_microservice/.env.example`](./properties_microservice/.env.example) |
| **03 - Gestión de Reservas** `reservations_microservice` | ✅ Implementado | Node.js · Express · MongoDB 6 · Mongoose · Joi · Axios | `3000` → `localhost:3000` (`server.js:6`, `docker-compose.yml:14`) | `27017` → `localhost:27018` | [`reservations_microservice/README.md`](./reservations_microservice/README.md) | [`reservations_microservice/.env.example`](./reservations_microservice/.env.example) |
| **04 - Agregador / Dashboard** `dashboard_microservice` | ⏳ Placeholder | *Por definir* (sin BD propia) | — | — | — | — |
| **05 - Consultas Analíticas** `analytics_microservice` | ⏳ Placeholder | Python (boto3) + AWS Athena | — | — | — | — |

> Los 3 microservicios implementados ya exponen CRUD completo, validaciones cruzadas (Reservas → Usuarios/Propiedades), Swagger/ReDoc y scripts de 20.000 registros. Dashboard y Analytics solo contienen `Dockerfile` vacío — están descritos por spec pero sin código aún.

---

## 🏗️ Arquitectura de Microservicios (Backend)

*   **Gestión de Usuarios (`user_microservice`):** Registra, autentica (JWT HS256) y gestiona perfiles `HUESPED`/`ANFITRION` + métodos de pago. Ver [`user_microservice/README.md`](./user_microservice/README.md) — endpoints `POST /usuarios/`, `GET /usuarios/{id}`, `POST /usuarios/{id}/metodos-pago/`, `POST /login/`.
    *   *Tecnología:* Python (FastAPI) y PostgreSQL.
*   **Catálogo de Propiedades (`properties_microservice`):** CRUD de anuncios con ubicación 1:1, borrado lógico (`INACTIVO`). Ver [`properties_microservice/README.md`](./properties_microservice/README.md) — endpoints `POST/GET /properties`, `GET/PUT/DELETE /properties/{id}`.
    *   *Tecnología:* Java (Spring Boot) y MySQL.
*   **Gestión de Reservas (`reservations_microservice`):** Reservas y reseñas; valida huésped (MS1) y propiedad (MS2) antes de confirmar y calcula `precio_total`. Ver [`reservations_microservice/README.md`](./reservations_microservice/README.md) — endpoints `POST /reservas/`, `GET /reservas/:id`, `GET /reservas/huesped/:id`, `PATCH /reservas/:id/estado`, `POST /resenas/`, `GET /resenas/propiedad/:id`.
    *   *Tecnología:* Node.js y MongoDB.
*   **Agregador / Dashboard (`dashboard_microservice`):** Servicio intermediario sin BD propia. Recibe peticiones complejas desde el frontend y consulta de manera síncrona a Usuarios, Propiedades y Reservas para consolidar la información. *(placeholder)*
*   **Consultas Analíticas (`analytics_microservice`):** Provee endpoints REST que exponen métricas y estadísticas del negocio, ejecutando consultas SQL directamente sobre AWS Athena. *(placeholder)*
    *   *Tecnología:* Python (boto3).

---

## 🗂️ Estructura del repositorio

```
Proyecto_Cloud/
├── user_microservice/          # MS1 - ver README específico
│   ├── app/ (main.py, models.py, schemas.py, crud.py)
│   ├── scripts/generate_fake_data.py
│   ├── .env.example            # ← plantilla (copiar a .env)
│   └── README.md
├── properties_microservice/    # MS2 - ver README específico
│   ├── src/main/java/.../controller/PropertyController.java
│   ├── src/main/resources/application.yml
│   ├── scripts/generate_fake_data.py
│   ├── .env.example
│   └── README.md
├── reservations_microservice/  # MS3 - ver README específico
│   ├── app/ (main.js, routes/, services.js, schemas.js)
│   ├── scripts/generate_fake_data.js
│   ├── .env.example
│   └── README.md
├── dashboard_microservice/     # placeholder (Dockerfile vacío)
├── analytics_microservice/     # placeholder (Dockerfile vacío)
├── Proyecto_Cloud.postman_collection.json  # Colección Postman general (5 carpetas)
└── README.md                   # Este archivo
```

Cada microservicio es auto-contenido con su propio `docker-compose.yml`, `Dockerfile`, `init.sql` (cuando aplica) y `.env.example`. Ver READMEs individuales para instrucciones detalladas.

---

## ⚙️ Configuración rápida (`.env.example` → `.env`)

Todos los servicios implementados usan plantilla versionada `.env.example` → copiar a `.env`:

```bash
# MS1
cp user_microservice/.env.example user_microservice/.env
# MS2
cp properties_microservice/.env.example properties_microservice/.env
# MS3
cp reservations_microservice/.env.example reservations_microservice/.env
```

| Servicio | Plantilla | Variables clave |
|---|---|---|
| MS1 Usuarios | [`user_microservice/.env.example`](./user_microservice/.env.example) | `DATABASE_URL`, `POSTGRES_USER/PASSWORD/DB`, `JWT_SECRET_KEY/ALGORITHM/EXPIRATION` — ver [user_microservice/README.md §2](./user_microservice/README.md#2-variables-de-entorno-env--envexample) |
| MS2 Propiedades | [`properties_microservice/.env.example`](./properties_microservice/.env.example) | `DB_HOST/PORT/NAME/USER/PASSWORD`, `MYSQL_ROOT_PASSWORD`, `SERVER_PORT`, `JPA_DDL_AUTO` — ver [properties_microservice/README.md §Variables](./properties_microservice/README.md#variables-de-entorno-env--envexample) |
| MS3 Reservas | [`reservations_microservice/.env.example`](./reservations_microservice/.env.example) | `PORT`, `MONGODB_URI`, `USER_SERVICE_URL`, `PROPERTY_SERVICE_URL` — ver [reservations_microservice/README.md §Variables](./reservations_microservice/README.md#variables-de-entorno-env--envexample) |

> **Puertos host:** MS1 `8000`/`5433`, MS2 `8081`/`3307`, MS3 `3000`/`27018`. Si tienes conflictos, ajusta los mapeos en cada `docker-compose.yml` y los `.env`. Para inter-comunicación en Docker con compose separados, MS3 usa `host.docker.internal:8000/8081` (ver su `.env.example` Opción A/B).

---

## 🚀 Ejecución por microservicio

> Cada servicio se levanta de forma independiente (cada uno con su propio `docker-compose.yml`). Para validación cruzada de Reservas, levanta MS1 y MS2 primero.

```bash
# MS1 - Usuarios (http://localhost:8000/docs)
cd user_microservice && cp .env.example .env && docker compose up --build

# MS2 - Propiedades (http://localhost:8081/swagger-ui.html)
cd properties_microservice && cp .env.example .env && docker compose up --build

# MS3 - Reservas (http://localhost:3000)
cd reservations_microservice && cp .env.example .env && docker compose up --build
```

Ver secciones **Ejecución** en cada README para flujo manual sin Docker y poblado de 20.000 registros:
*   [user_microservice - Ejecución](./user_microservice/README.md#4-ejecución) + [Datos de prueba](./user_microservice/README.md#7-datos-de-prueba-20000-registros)
*   [properties_microservice - Ejecución](./properties_microservice/README.md#ejecución-con-docker-compose-recomendado) + [Poblar datos](./properties_microservice/README.md#poblar-datos-de-prueba-20000-registros)
*   [reservations_microservice - Ejecución](./reservations_microservice/README.md#ejecución-con-docker-compose-recomendado) + [Generar datos](./reservations_microservice/README.md#generar-datos-de-prueba-20000-registros)

---

## 📮 Colección Postman

Colección general versionada en [`Proyecto_Cloud.postman_collection.json`](./Proyecto_Cloud.postman_collection.json) — generada inspeccionando `app/main.py`, `PropertyController.java`, `app/routes/*.js` y `docker-compose.yml`.

*   **5 carpetas por microservicio** (3 implementados con requests reales + 2 placeholder para Dashboard/Analytics)
*   **Variables:** `{{user_baseUrl}}` (`http://localhost:8000`), `{{properties_baseUrl}}` (`http://localhost:8081`), `{{reservations_baseUrl}}` (`http://localhost:3000`), `{{dashboard_baseUrl}}`/`{{analytics_baseUrl}}`
*   **22 requests** totales — ver descripción dentro del JSON para origen de cada endpoint (`main.py:16`, `PropertyController.java:30`, `reservas.routes.js:16`, etc.)
*   Importar en Postman: `File → Import → Proyecto_Cloud.postman_collection.json`

---

## 🖥️ Frontend (UI)

La interfaz de usuario es una Single-Page Application (SPA) construida en React o Angular y desplegada mediante **AWS Amplify**. La aplicación web se comunica con el backend a través de AWS API Gateway (mediante HTTPS), consumiendo al menos 2 métodos REST de cada uno de los 5 microservicios.

---

## 📊 Data Science & Analytics

El procesamiento analítico cuenta con una Máquina Virtual exclusiva dedicada a la ingesta de datos.
*   **Extracción:** Tres contenedores Docker en Python ejecutan una estrategia pull para extraer el 100% de la data transaccional y cargarla en formato CSV/JSON hacia un bucket S3.
*   **Catálogo y Análisis:** Se implementa un catálogo de datos en AWS Glue. Las consultas de métricas y vistas del negocio se generan cruzando información (JOINs) nativamente con AWS Athena.

---

## 🚀 Despliegue e Infraestructura

*   **Entorno de Producción:** Los microservicios operan sobre dos Máquinas Virtuales (MV) con un balanceador de carga privado. Todas las bases de datos residen en una tercera MV de acceso estrictamente privado.
*   **Documentación de APIs:** Todos los servicios exponen su documentación estándar mediante Swagger-UI (`/docs` y `/swagger-ui.html`; Reservas sin Swagger por ser Express).
*   **Datos de Prueba:** Los entornos de base de datos están poblados con un mínimo de 20,000 registros ficticios insertados masivamente para pruebas de estrés y analítica (ver READMEs individuales).

---

## 📚 Documentación por servicio

*   [User Microservice — gestión de usuarios, auth y pagos](./user_microservice/README.md)
*   [Properties Microservice — catálogo de propiedades](./properties_microservice/README.md)
*   [Reservations Microservice — reservas y reseñas](./reservations_microservice/README.md)
*   Dashboard & Analytics — pendientes de implementación (ver placeholders en Postman collection)
