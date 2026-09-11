const Joi = require('joi');

// --- Esquema para crear una reserva ---
// precio_total NO se recibe del cliente: se calcula internamente a partir
// del precio_noche que devuelve el MS2 (Catálogo de Propiedades).
const reservaCreateSchema = Joi.object({
  id_huesped: Joi.string().trim().min(1).required().messages({
    'any.required': 'id_huesped es obligatorio',
    'string.empty': 'id_huesped no puede estar vacío'
  }),
  id_propiedad: Joi.number().integer().positive().required().messages({
    'any.required': 'id_propiedad es obligatorio'
  }),
  fecha_checkin: Joi.date().iso().required().messages({
    'any.required': 'fecha_checkin es obligatoria'
  }),
  fecha_checkout: Joi.date().iso().greater(Joi.ref('fecha_checkin')).required().messages({
    'any.required': 'fecha_checkout es obligatoria',
    'date.greater': 'fecha_checkout debe ser posterior a fecha_checkin'
  })
});

// --- Esquema para reemplazar una reserva (PUT) ---
// PUT reemplaza el recurso completo: exige los mismos campos que la creación.
// estado_reserva es opcional; si no se envía, se conserva el valor actual.
const reservaUpdateSchema = reservaCreateSchema.keys({
  estado_reserva: Joi.string()
    .valid('PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'COMPLETADA')
    .optional()
});
// --- Esquema para crear una reseña ---
const resenaCreateSchema = Joi.object({
  id_reserva: Joi.string().length(24).hex().required().messages({
    'any.required': 'id_reserva es obligatorio',
    'string.length': 'id_reserva no tiene un formato válido'
  }),
  calificacion: Joi.number().integer().min(1).max(5).required(),
  comentario: Joi.string().max(500).allow('', null)
});

module.exports = {
  reservaCreateSchema,
  reservaUpdateSchema,
  resenaCreateSchema
};