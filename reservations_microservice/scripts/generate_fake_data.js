require('dotenv').config();

const mongoose = require('mongoose');
const { faker } = require('@faker-js/faker');
const { Reserva } = require('../app/models');

const MONGODB_URI = process.env.MONGODB_URI;

const ESTADOS = ['PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'COMPLETADA'];
const TOTAL_REGISTROS = 20000;
const TAMANO_LOTE = 5000;

async function populateData() {
  await mongoose.connect(MONGODB_URI);
  console.log('Iniciando generación e inserción de 20,000 registros de reservas...');

  let lote = [];

  for (let i = 1; i <= TOTAL_REGISTROS; i += 1) {
    const fechaCheckin = faker.date.soon({ days: 180 });
    const fechaCheckout = new Date(fechaCheckin);
    fechaCheckout.setDate(fechaCheckout.getDate() + faker.number.int({ min: 1, max: 14 }));

    lote.push({
      // Simula un uuid del MS1 (no se valida contra el MS1 real: es data de prueba masiva)
      id_huesped: faker.string.uuid(),
      // Simula un id_propiedad del MS2
      id_propiedad: faker.number.int({ min: 1, max: 5000 }),
      fecha_checkin: fechaCheckin,
      fecha_checkout: fechaCheckout,
      precio_total: Number(faker.commerce.price({ min: 50, max: 3000 })),
      estado_reserva: faker.helpers.arrayElement(ESTADOS),
      fecha_creacion: faker.date.recent({ days: 90 })
    });

    // Insertar en bloques de 5,000 para optimizar el rendimiento
    if (lote.length === TAMANO_LOTE) {
      await Reserva.insertMany(lote, { ordered: false });
      console.log(`${i} registros insertados...`);
      lote = [];
    }
  }

  console.log('Proceso de carga masiva completado con éxito.');
  await mongoose.disconnect();
}

populateData().catch((err) => {
  console.error('Error durante la generación de datos de prueba:', err);
  process.exit(1);
});
