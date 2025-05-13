/**
 * Global error handling middleware
 */

const logger = require('../utils/logger');

/**
 * Error handling middleware for the MCP server
 * 
 * @param {Error} err - The error object
 * @param {Express.Request} req - Express request object
 * @param {Express.Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const errorHandler = (err, req, res, next) => {
  // Default error status and message
  const status = err.status || err.statusCode || 500;
  const message = err.message || 'Internal Server Error';

  // Log the error based on severity
  if (status >= 500) {
    logger.error(`${status} - ${message}`, {
      stack: err.stack,
      path: req.path,
      method: req.method,
      ip: req.ip,
    });
  } else {
    logger.warn(`${status} - ${message}`, {
      path: req.path,
      method: req.method,
      ip: req.ip,
    });
  }

  // Avoid exposing internal details in production
  const response = {
    status: 'error',
    code: status,
    message,
  };

  // Include stack trace in development
  if (process.env.NODE_ENV === 'development' && err.stack) {
    response.stack = err.stack.split('\n');
  }

  // Include validation errors if present
  if (err.errors) {
    response.errors = err.errors;
  }

  // Send response
  res.status(status).json(response);
};

module.exports = errorHandler;