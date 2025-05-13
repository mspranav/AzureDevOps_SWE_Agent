/**
 * Custom error classes for the MCP server
 */

/**
 * Base API error class
 */
class ApiError extends Error {
  /**
   * Create a new API error
   * @param {string} message - Error message
   * @param {number} statusCode - HTTP status code
   * @param {Array} errors - Validation errors
   */
  constructor(message, statusCode = 500, errors = null) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = statusCode;
    this.errors = errors;
    Error.captureStackTrace(this, this.constructor);
  }
}

/**
 * 400 Bad Request error
 */
class BadRequestError extends ApiError {
  /**
   * Create a new bad request error
   * @param {string} message - Error message
   * @param {Array} errors - Validation errors
   */
  constructor(message = 'Bad Request', errors = null) {
    super(message, 400, errors);
  }
}

/**
 * 401 Unauthorized error
 */
class UnauthorizedError extends ApiError {
  /**
   * Create a new unauthorized error
   * @param {string} message - Error message
   */
  constructor(message = 'Unauthorized') {
    super(message, 401);
  }
}

/**
 * 403 Forbidden error
 */
class ForbiddenError extends ApiError {
  /**
   * Create a new forbidden error
   * @param {string} message - Error message
   */
  constructor(message = 'Forbidden') {
    super(message, 403);
  }
}

/**
 * 404 Not Found error
 */
class NotFoundError extends ApiError {
  /**
   * Create a new not found error
   * @param {string} message - Error message
   */
  constructor(message = 'Resource not found') {
    super(message, 404);
  }
}

/**
 * 409 Conflict error
 */
class ConflictError extends ApiError {
  /**
   * Create a new conflict error
   * @param {string} message - Error message
   */
  constructor(message = 'Resource conflict') {
    super(message, 409);
  }
}

/**
 * 429 Too Many Requests error
 */
class TooManyRequestsError extends ApiError {
  /**
   * Create a new too many requests error
   * @param {string} message - Error message
   */
  constructor(message = 'Too many requests') {
    super(message, 429);
  }
}

/**
 * 500 Internal Server error
 */
class InternalServerError extends ApiError {
  /**
   * Create a new internal server error
   * @param {string} message - Error message
   */
  constructor(message = 'Internal Server Error') {
    super(message, 500);
  }
}

/**
 * 502 Bad Gateway error
 */
class BadGatewayError extends ApiError {
  /**
   * Create a new bad gateway error
   * @param {string} message - Error message
   */
  constructor(message = 'Bad Gateway') {
    super(message, 502);
  }
}

/**
 * 503 Service Unavailable error
 */
class ServiceUnavailableError extends ApiError {
  /**
   * Create a new service unavailable error
   * @param {string} message - Error message
   */
  constructor(message = 'Service Unavailable') {
    super(message, 503);
  }
}

/**
 * 504 Gateway Timeout error
 */
class GatewayTimeoutError extends ApiError {
  /**
   * Create a new gateway timeout error
   * @param {string} message - Error message
   */
  constructor(message = 'Gateway Timeout') {
    super(message, 504);
  }
}

module.exports = {
  ApiError,
  BadRequestError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
  ConflictError,
  TooManyRequestsError,
  InternalServerError,
  BadGatewayError,
  ServiceUnavailableError,
  GatewayTimeoutError,
};