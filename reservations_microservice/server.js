require('dotenv').config();

const app = require('./app/main');
const { connectDB } = require('./app/database');

const PORT = process.env.PORT || 3000;

const startServer = async () => {
  await connectDB();
  app.listen(PORT, () => {
    console.log(`Microservicio de Reservas escuchando en el puerto ${PORT}`);
  });
};

startServer();
