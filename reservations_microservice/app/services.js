const axios = require('axios');
require('dotenv').config();

// URLs configurables por variable de entorno, siguiendo el mismo patrón
// que user_microservice usa para DATABASE_URL: nada de rutas fijas en el código.
const USER_SERVICE_URL = process.env.USER_SERVICE_URL;
const PROPERTY_SERVICE_URL = process.env.PROPERTY_SERVICE_URL;

const REQUEST_TIMEOUT_MS = 5000;

class ExternalServiceError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.name = 'ExternalServiceError';
    this.statusCode = statusCode;
  }
}

/**
 * Traduce cualquier error de axios (404 real, otros códigos HTTP, timeout,
 * DNS, conexión rechazada, etc.) a un ExternalServiceError con un status
 * HTTP apropiado para que el controlador solo tenga que reenviarlo.
 */
function mapAxiosError(error, entidad) {
  if (error.response) {
    if (error.response.status === 404) {
      return new ExternalServiceError(`${entidad} no existe`, 404);
    }
    return new ExternalServiceError(
      `El servicio externo respondió con un error inesperado (${error.response.status})`,
      502
    );
  }
  // No hubo respuesta: timeout, servicio caído, DNS, red, etc.
  return new ExternalServiceError(
    `No fue posible comunicarse con el servicio externo (${entidad})`,
    503
  );
}

/**
 * Valida un huésped contra el MS1 (Gestión de Usuarios).
 * Usa el contrato real ya implementado: GET /usuarios/{usuario_id}
 * Devuelve el usuario si existe; lanza ExternalServiceError si no.
 */
async function getUsuario(idUsuario) {
  try {
    const { data } = await axios.get(`${USER_SERVICE_URL}/usuarios/${idUsuario}`, {
      timeout: REQUEST_TIMEOUT_MS
    });
    return data;
  } catch (error) {
    throw mapAxiosError(error, 'El usuario (huésped)');
  }
}

/**
 * Valida una propiedad contra el MS2 (Catálogo de Propiedades, Spring Boot).
 * Contrato real: GET /properties/{id} devolviendo JSON con "precioNoche"
 * (se acepta también "precio_noche" por compatibilidad).
 */
async function getPropiedad(idPropiedad) {
  try {
    const { data } = await axios.get(`${PROPERTY_SERVICE_URL}/properties/${idPropiedad}`, {
      timeout: REQUEST_TIMEOUT_MS
    });
    return data;
  } catch (error) {
    throw mapAxiosError(error, 'La propiedad');
  }
}

module.exports = { getUsuario, getPropiedad, ExternalServiceError };
