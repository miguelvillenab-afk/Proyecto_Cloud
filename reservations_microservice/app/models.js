const mongoose = require('mongoose');
const { Schema } = mongoose;

const ESTADOS_RESERVA = ['PENDIENTE', 'CONFIRMADA', 'CANCELADA', 'COMPLETADA'];

/**
 * Colección: Reservas
 * id_huesped   -> UUID del usuario, referencia lógica al MS1 (Usuarios)
 * id_propiedad -> ID numérico de la propiedad, referencia lógica al MS2 (Propiedades)
 */
const reservaSchema = new Schema({
  id_huesped: {
    type: String,
    required: [true, 'El id_huesped es obligatorio'],
    trim: true
  },
  id_propiedad: {
    type: Number,
    required: [true, 'El id_propiedad es obligatorio']
  },
  fecha_checkin: {
    type: Date,
    required: [true, 'La fecha de check-in es obligatoria']
  },
  fecha_checkout: {
    type: Date,
    required: [true, 'La fecha de check-out es obligatoria']
  },
  precio_total: {
    type: Number,
    required: [true, 'El precio total es obligatorio'],
    min: [0, 'El precio total no puede ser negativo']
  },
  estado_reserva: {
    type: String,
    enum: ESTADOS_RESERVA,
    default: 'PENDIENTE'
  },
  fecha_creacion: {
    type: Date,
    default: Date.now
  }
});

// La fecha de checkout siempre debe ser posterior a la de checkin
reservaSchema.pre('validate', function preValidate(next) {
  if (this.fecha_checkin && this.fecha_checkout && this.fecha_checkout <= this.fecha_checkin) {
    return next(new Error('La fecha de checkout debe ser posterior a la fecha de checkin'));
  }
  return next();
});

/**
 * Colección: Resenas
 * id_reserva -> referencia a un documento de la colección Reservas
 */
const resenaSchema = new Schema({
  id_reserva: {
    type: Schema.Types.ObjectId,
    ref: 'Reserva',
    required: [true, 'El id_reserva es obligatorio']
  },
  id_propiedad: {
    type: Number,
    required: [true, 'El id_propiedad es obligatorio']
  },
  id_huesped: {
    type: String,
    required: [true, 'El id_huesped es obligatorio'],
    trim: true
  },
  calificacion: {
    type: Number,
    required: [true, 'La calificación es obligatoria'],
    min: [1, 'La calificación mínima es 1'],
    max: [5, 'La calificación máxima es 5']
  },
  comentario: {
    type: String,
    trim: true,
    maxlength: 500
  },
  fecha_creacion: {
    type: Date,
    default: Date.now
  }
});

const Reserva = mongoose.model('Reserva', reservaSchema, 'reservas');
const Resena = mongoose.model('Resena', resenaSchema, 'resenas');

module.exports = { Reserva, Resena, ESTADOS_RESERVA };
