const { Reserva, Resena } = require('./models');

// --- Reservas ---

async function createReserva(data) {
  const reserva = new Reserva(data);
  return reserva.save();
}

async function getReservaById(id) {
  return Reserva.findById(id);
}

async function getReservasByHuesped(idHuesped) {
  return Reserva.find({ id_huesped: idHuesped }).sort({ fecha_creacion: -1 });
}

async function updateEstadoReserva(id, estado) {
  return Reserva.findByIdAndUpdate(
    id,
    { estado_reserva: estado },
    { new: true, runValidators: true }
  );
}

// --- Resenas ---

async function createResena(data) {
  const resena = new Resena(data);
  return resena.save();
}

async function getResenasByPropiedad(idPropiedad) {
  return Resena.find({ id_propiedad: idPropiedad }).sort({ fecha_creacion: -1 });
}

module.exports = {
  createReserva,
  getReservaById,
  getReservasByHuesped,
  updateEstadoReserva,
  createResena,
  getResenasByPropiedad
};
