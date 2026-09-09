const express = require('express');
const router = express.Router();

const crud = require('../crud');
const { getUsuario, getPropiedad, ExternalServiceError } = require('../services');
const { reservaCreateSchema, reservaEstadoUpdateSchema } = require('../schemas');

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
    // 1. Validar usuario contra MS1
    await getUsuario(id_huesped);

    // 2. Validar propiedad contra MS2
    const propiedad = await getPropiedad(id_propiedad);
    const precioNoche = propiedad.precio_noche ?? propiedad.precioNoche;

    if (precioNoche === undefined || precioNoche === null) {
      return res.status(502).json({
        detail: 'El microservicio de propiedades no devolvió un precio_noche válido'
      });
    }

    // 3. Calcular el valor total de la reserva
    const nochesSolicitadas = Math.round(
      (new Date(fecha_checkout) - new Date(fecha_checkin)) / (1000 * 60 * 60 * 24)
    );
    const precio_total = Number((nochesSolicitadas * precioNoche).toFixed(2));

    // 4. Crear la reserva
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
    if (err instanceof ExternalServiceError) {
      return res.status(err.statusCode).json({ detail: err.message });
    }
    if (err.name === 'ValidationError') {
      return res.status(400).json({ detail: err.message });
    }
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al crear la reserva' });
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
 * PATCH /reservas/:id/estado
 * Actualiza el estado de una reserva (p.ej. CANCELADA, COMPLETADA).
 */
router.patch('/:id/estado', async (req, res) => {
  const { error, value } = reservaEstadoUpdateSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ detail: error.details[0].message });
  }

  try {
    const reserva = await crud.updateEstadoReserva(req.params.id, value.estado_reserva);
    if (!reserva) {
      return res.status(404).json({ detail: 'Reserva no encontrada' });
    }
    return res.json(reserva);
  } catch (err) {
    if (err.name === 'CastError') {
      return res.status(400).json({ detail: 'El id de reserva no tiene un formato válido' });
    }
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al actualizar la reserva' });
  }
});

module.exports = router;
