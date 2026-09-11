const express = require('express');
const router = express.Router();

const crud = require('../crud');
const { getUsuario, getPropiedad, ExternalServiceError } = require('../services');
const { reservaCreateSchema, reservaUpdateSchema } = require('../schemas');

/**
 * Valida usuario (MS1) y propiedad (MS2), y calcula el precio_total.
 * Se reutiliza tanto en POST (creación) como en PUT (reemplazo), porque
 * en ambos casos se está fijando el estado completo de la reserva y por
 * lo tanto deben repetirse las dos validaciones externas.
 */
async function validarYCalcularPrecio(id_huesped, id_propiedad, fecha_checkin, fecha_checkout) {
  // 1. Validar usuario contra MS1
  await getUsuario(id_huesped);

  // 2. Validar propiedad contra MS2
  const propiedad = await getPropiedad(id_propiedad);
  const precioNoche = propiedad.precio_noche ?? propiedad.precioNoche;

  if (precioNoche === undefined || precioNoche === null) {
    const err = new Error('El microservicio de propiedades no devolvió un precio_noche válido');
    err.statusCode = 502;
    throw err;
  }

  // 3. Calcular el valor total según las noches solicitadas
  const noches = Math.round(
    (new Date(fecha_checkout) - new Date(fecha_checkin)) / (1000 * 60 * 60 * 24)
  );
  return Number((noches * precioNoche).toFixed(2));
}

function manejarErroresComunes(err, res, mensajePorDefecto) {
  if (err instanceof ExternalServiceError) {
    return res.status(err.statusCode).json({ detail: err.message });
  }
  if (err.statusCode) {
    return res.status(err.statusCode).json({ detail: err.message });
  }
  if (err.name === 'CastError') {
    return res.status(400).json({ detail: 'El id de reserva no tiene un formato válido' });
  }
  if (err.name === 'ValidationError') {
    return res.status(400).json({ detail: err.message });
  }
  console.error(err);
  return res.status(500).json({ detail: mensajePorDefecto });
}
  

/**
 * POST /reservas/
 * Crea una nueva reserva.
 * 1. Valida al huésped contra el MS1 (GET /usuarios/{id}).
 * 2. Valida la propiedad contra el MS2 (GET /propiedades/{id}) y obtiene su precio_noche.
 * 3. Calcula el precio_total según las noches solicitadas.
 * 4. Persiste la reserva en MongoDB.
 */
router.post('/', async (req, res) => {
  const { error, value } = reservaCreateSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ detail: error.details[0].message });
  }

  const { id_huesped, id_propiedad, fecha_checkin, fecha_checkout } = value;

  try {
    const precio_total = await validarYCalcularPrecio(
      id_huesped, id_propiedad, fecha_checkin, fecha_checkout
    );

    const reserva = await crud.createReserva({
      id_huesped,
      id_propiedad,
      fecha_checkin,
      fecha_checkout,
      precio_total,
      estado_reserva: 'CONFIRMADA'
    });

    return res.status(201).json(reserva);
  } catch (err) {
    return manejarErroresComunes(err, res, 'Error interno al crear la reserva');
  }
});

/**
 * GET /reservas/huesped/:id_huesped
 * Lista todas las reservas realizadas por un huésped.
 * (Definida antes de /:id para que Express no la interprete como un ObjectId).
 */
router.get('/huesped/:id_huesped', async (req, res) => {
  try {
    const reservas = await crud.getReservasByHuesped(req.params.id_huesped);
    return res.json(reservas);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al obtener las reservas' });
  }
});

/**
 * GET /reservas/:id
 * Obtiene una reserva por su ObjectId de MongoDB.
 */
router.get('/:id', async (req, res) => {
  try {
    const reserva = await crud.getReservaById(req.params.id);
    if (!reserva) {
      return res.status(404).json({ detail: 'Reserva no encontrada' });
    }
    return res.json(reserva);
  } catch (err) {
    if (err.name === 'CastError') {
      return res.status(400).json({ detail: 'El id de reserva no tiene un formato válido' });
    }
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al obtener la reserva' });
  }
});


/**
 * PUT /reservas/:id
 * Reemplaza una reserva existente (id_huesped, id_propiedad, fechas y,
 * opcionalmente, estado_reserva). Como PUT redefine el recurso completo
 * -incluyendo quién reserva y qué propiedad- SIEMPRE se vuelve a validar
 * contra MS1 y MS2, y el precio_total se recalcula desde cero (nunca se
 * confía en un precio enviado por el cliente).
 */
router.put('/:id', async (req, res) => {
  const { error, value } = reservaUpdateSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ detail: error.details[0].message });
  }

  try {
    const existente = await crud.getReservaById(req.params.id);
    if (!existente) {
      return res.status(404).json({ detail: 'Reserva no encontrada' });
    }

    const { id_huesped, id_propiedad, fecha_checkin, fecha_checkout, estado_reserva } = value;

    const precio_total = await validarYCalcularPrecio(
      id_huesped, id_propiedad, fecha_checkin, fecha_checkout
    );

    const reserva = await crud.replaceReserva(req.params.id, {
      id_huesped,
      id_propiedad,
      fecha_checkin,
      fecha_checkout,
      precio_total,
      estado_reserva: estado_reserva || existente.estado_reserva
    });

    return res.json(reserva);
  } catch (err) {
    return manejarErroresComunes(err, res, 'Error interno al actualizar la reserva');
  }
});

/**
 * DELETE /reservas/:id
 * Elimina una reserva. Se implementa como borrado lógico (estado_reserva
 * pasa a CANCELADA), el mismo criterio que ya usa properties_microservice
 * con su campo "estado" al eliminar una propiedad. Esto conserva el
 * historial para la capa analítica (MS5 / Athena) en vez de perder datos.
 */
router.delete('/:id', async (req, res) => {
  try {
    const reserva = await crud.cancelReserva(req.params.id);
    if (!reserva) {
      return res.status(404).json({ detail: 'Reserva no encontrada' });
    }
    return res.status(204).send();
  } catch (err) {
    return manejarErroresComunes(err, res, 'Error interno al eliminar la reserva');
  }
});

module.exports = router;