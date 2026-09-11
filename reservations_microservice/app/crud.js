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

// PUT: reemplaza los campos del recurso (precio_total ya viene recalculado
// por el controlador). No se toca _id ni fecha_creacion.
async function replaceReserva(id, data) {
  return Reserva.findByIdAndUpdate(id, data, { new: true, runValidators: true });
}


// DELETE: borrado lógico (mismo criterio que properties_microservice con
// su campo "estado"). Conserva el historial para la capa analítica.
async function cancelReserva(id) {
  return Reserva.findByIdAndUpdate(
    id,
    { estado_reserva: 'CANCELADA' },
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
  replaceReserva,
  cancelReserva,
  createResena,
  getResenasByPropiedad
};
