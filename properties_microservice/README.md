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

## Requisitos previos

- **Docker** y **Docker Compose** instalados
- **Java 17+** y **Maven** (si se ejecuta sin Docker)

## Ejecución con Docker Compose (recomendado)

```bash
cd properties_microservice
cp .env.example .env      # y ajusta las contraseñas
docker compose up --build
```

- API: `http://localhost:8081`
- MySQL expuesto en el host: `localhost:3307`

## Poblar datos de prueba (20,000 registros)

```bash
cd scripts
pip install -r requirements.txt
# Crea un .env en scripts/ (o exporta las variables) con los mismos datos que el .env de arriba
python generate_fake_data.py
```

Genera `propiedades` con anfitriones aleatorios y su `ubicacion` 1:1 correspondiente.

## Notas para el despliegue en AWS

- Todo se configura por variables de entorno (`DB_HOST`, `DB_PORT`, etc.), así que en producción
  solo hay que apuntar `DB_HOST` a la MySQL de la 3ra MV privada.
- Swagger queda disponible para documentar la API que se expone vía AWS API Gateway.
