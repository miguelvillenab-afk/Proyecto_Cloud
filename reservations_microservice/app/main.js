const express = require('express');
const cors = require('cors');

const reservasRoutes = require('./routes/reservas.routes');
const resenasRoutes = require('./routes/resenas.routes');

const app = express();

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {
  res.json({
    servicio: 'API de Gestión de Reservas (Microservicio 3)',
    descripcion: 'Microservicio de reservas y reseñas. Valida usuarios y propiedades consumiendo MS1 y MS2.',
    version: '1.0.0'
  });
});

app.use('/reservas', reservasRoutes);
app.use('/resenas', resenasRoutes);

// Ruta no encontrada
app.use((req, res) => {
  res.status(404).json({ detail: 'Ruta no encontrada' });
});

// Manejador de errores (p.ej. JSON mal formado en el body)
// eslint-disable-next-line no-unused-vars
app.use((err, req, res, next) => {
  if (err.type === 'entity.parse.failed') {
    return res.status(400).json({ detail: 'El cuerpo de la petición no es un JSON válido' });
  }
  console.error(err);
  return res.status(500).json({ detail: 'Error interno del servidor' });
});

module.exports = app;
