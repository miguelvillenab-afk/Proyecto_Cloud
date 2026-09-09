const mongoose = require('mongoose');
require('dotenv').config();

const MONGODB_URI = process.env.MONGODB_URI;

/**
 * Abre la conexión a MongoDB usando la URI configurada en las variables
 * de entorno. Sigue el mismo patrón que database.py del user_microservice:
 * la cadena de conexión se lee exclusivamente desde el .env.
 */
const connectDB = async () => {
  if (!MONGODB_URI) {
    console.error('La variable de entorno MONGODB_URI no está definida.');
    process.exit(1);
  }

  try {
    await mongoose.connect(MONGODB_URI);
    console.log('Conexión a MongoDB establecida correctamente.');
  } catch (error) {
    console.error('Error al conectar con MongoDB:', error.message);
    process.exit(1);
  }
};

module.exports = { connectDB };
