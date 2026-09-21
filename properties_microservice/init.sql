CREATE TABLE IF NOT EXISTS propiedades (
    id_propiedad   BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_anfitrion   VARCHAR(255)   NOT NULL,
    titulo         VARCHAR(200)   NOT NULL,
    precio_noche   DECIMAL(10,2)  NOT NULL,
    capacidad      INT            NOT NULL,
    estado         VARCHAR(20)    NOT NULL DEFAULT 'ACTIVO'
);

CREATE TABLE IF NOT EXISTS ubicaciones (
    id_ubicacion   BIGINT AUTO_INCREMENT PRIMARY KEY,
    id_propiedad   BIGINT NOT NULL UNIQUE,
    pais           VARCHAR(100) NOT NULL,
    ciudad         VARCHAR(100) NOT NULL,
    direccion      VARCHAR(255) NOT NULL,
    FOREIGN KEY (id_propiedad) REFERENCES propiedades(id_propiedad) ON DELETE CASCADE
);
