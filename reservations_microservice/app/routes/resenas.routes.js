const express = require('express');
const router = express.Router();

const crud = require('../crud');
const { resenaCreateSchema } = require('../schemas');

/**
 * POST /resenas/
 * Crea una reseña asociada a una reserva ya existente.
 * id_propiedad e id_huesped se derivan de la reserva encontrada,
 * no se confían al cliente, para evitar reseñas inconsistentes.
 */
router.post('/', async (req, res) => {
  const { error, value } = resenaCreateSchema.validate(req.body);
  if (error) {
    return res.status(400).json({ detail: error.details[0].message });
  }

  try {
    const reserva = await crud.getReservaById(value.id_reserva);
    if (!reserva) {
      return res.status(404).json({ detail: 'La reserva asociada no existe' });
    }

    const resena = await crud.createResena({
      id_reserva: reserva._id,
      id_propiedad: reserva.id_propiedad,
      id_huesped: reserva.id_huesped,
      calificacion: value.calificacion,
      comentario: value.comentario
    });

    return res.status(201).json(resena);
  } catch (err) {
    if (err.name === 'CastError') {
      return res.status(400).json({ detail: 'El id_reserva no tiene un formato válido' });
    }
    if (err.name === 'ValidationError') {
      return res.status(400).json({ detail: err.message });
    }
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al crear la reseña' });
  }
});

/**
 * GET /resenas/propiedad/:id_propiedad
 * Lista las reseñas de una propiedad.
 */
router.get('/propiedad/:id_propiedad', async (req, res) => {
  try {
    const resenas = await crud.getResenasByPropiedad(Number(req.params.id_propiedad));
    return res.json(resenas);
  } catch (err) {
    console.error(err);
    return res.status(500).json({ detail: 'Error interno al obtener las reseñas' });
  }
});

module.exports = router;
