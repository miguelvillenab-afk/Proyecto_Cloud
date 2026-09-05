# Proyecto Cloud Computing: Plataforma de Alquiler de Alojamientos

Plataforma integral de alquiler de alojamientos donde los usuarios interactúan como Anfitriones (para publicar propiedades) o Huéspedes (para buscar y reservar). El sistema permite gestionar perfiles, publicar anuncios, realizar reservas y analizar el rendimiento del negocio mediante métricas avanzadas.

## 🏗️ Arquitectura de Microservicios (Backend)

El sistema backend está compuesto por 5 microservicios orquestados mediante Docker Compose y distribuidos según sus dominios de datos. 

*   **Gestión de Usuarios (`user_microservice`):** Registra, autentica y gestiona los perfiles de los huéspedes y anfitriones. 
    *   *Tecnología:* Python (FastAPI o Flask) y PostgreSQL.
*   **Catálogo de Propiedades (`properties_microservice`):** Administra las operaciones CRUD para los anuncios de alojamientos, gestionando descripciones, capacidades y precios. 
    *   *Tecnología:* Java (Spring Boot) y MySQL.
*   **Gestión de Reservas (`reservations_microservice`):** Maneja las solicitudes de reserva y valoraciones consumiendo internamente los servicios de usuarios y propiedades para las validaciones. 
    *   *Tecnología:* Node.js y MongoDB.
*   **Agregador / Dashboard (`dashboard_microservice`):** Actúa como servicio intermediario sin base de datos propia. Recibe peticiones complejas desde el frontend y consulta de manera síncrona a los microservicios de Usuarios, Propiedades y Reservas para consolidar la información.
*   **Consultas Analíticas (`analytics_microservice`):** Provee endpoints REST que exponen métricas y estadísticas del negocio, ejecutando consultas SQL directamente sobre AWS Athena. 
    *   *Tecnología:* Python (boto3).

## 🖥️ Frontend (UI)

La interfaz de usuario es una Single-Page Application (SPA) construida en React o Angular y desplegada mediante **AWS Amplify**. La aplicación web se comunica con el backend a través de AWS API Gateway (mediante HTTPS), consumiendo al menos 2 métodos REST de cada uno de los 5 microservicios.

## 📊 Data Science & Analytics

El procesamiento analítico cuenta con una Máquina Virtual exclusiva dedicada a la ingesta de datos.
*   **Extracción:** Tres contenedores Docker en Python ejecutan una estrategia pull para extraer el 100% de la data transaccional y cargarla en formato CSV/JSON hacia un bucket S3.
*   **Catálogo y Análisis:** Se implementa un catálogo de datos en AWS Glue. Las consultas de métricas y vistas del negocio se generan cruzando información (JOINs) nativamente con AWS Athena.

## 🚀 Despliegue e Infraestructura

*   **Entorno de Producción:** Los microservicios operan sobre dos Máquinas Virtuales (MV) con un balanceador de carga privado. Todas las bases de datos residen en una tercera MV de acceso estrictamente privado.
*   **Documentación de APIs:** Todos los servicios exponen su documentación estándar mediante Swagger-UI.
*   **Datos de Prueba:** Los entornos de base de datos están poblados con un mínimo de 20,000 registros ficticios insertados masivamente para pruebas de estrés y analítica.