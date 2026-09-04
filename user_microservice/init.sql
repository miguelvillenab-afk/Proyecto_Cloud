CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('HUESPED', 'ANFITRION')),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Metodos_Pago (
    id_metodo SERIAL PRIMARY KEY,
    id_usuario UUID NOT NULL,
    tipo_tarjeta VARCHAR(50) NOT NULL,
    ultimos_cuatro VARCHAR(4) NOT NULL,
    CONSTRAINT fk_usuario
        FOREIGN KEY(id_usuario) 
        REFERENCES Usuarios(id_usuario)
        ON DELETE CASCADE
);
