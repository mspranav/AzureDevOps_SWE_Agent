/**
 * Authentication middleware for the MCP server
 */

const jwt = require('jsonwebtoken');
const { ApiError } = require('../utils/errors');
const logger = require('../utils/logger');

/**
 * API key authentication middleware
 * 
 * @param {Express.Request} req - Express request object
 * @param {Express.Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const apiKeyAuth = (req, res, next) => {
  try {
    const apiKeyHeader = process.env.API_KEY_HEADER || 'X-API-Key';
    const apiKey = req.headers[apiKeyHeader.toLowerCase()];

    if (!apiKey) {
      throw new ApiError('API key is required', 401);
    }

    // In a real implementation, this would validate against stored API keys
    // For simplicity, we're using an environment variable
    const validApiKeys = process.env.VALID_API_KEYS ? process.env.VALID_API_KEYS.split(',') : [];
    
    if (process.env.NODE_ENV === 'development' && apiKey === 'dev-api-key') {
      // Allow a special dev key in development mode
      req.auth = { type: 'apiKey', id: 'development' };
      return next();
    }
    
    if (!validApiKeys.includes(apiKey)) {
      throw new ApiError('Invalid API key', 401);
    }

    // Attach auth info to request
    req.auth = { type: 'apiKey', id: apiKey };
    next();
  } catch (error) {
    next(error);
  }
};

/**
 * JWT authentication middleware
 * 
 * @param {Express.Request} req - Express request object
 * @param {Express.Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const jwtAuth = (req, res, next) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new ApiError('Authorization token is required', 401);
    }

    const token = authHeader.split(' ')[1];
    if (!token) {
      throw new ApiError('Invalid token format', 401);
    }

    // Verify token
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      
      // Check token expiration
      const now = Math.floor(Date.now() / 1000);
      if (decoded.exp && decoded.exp < now) {
        throw new ApiError('Token has expired', 401);
      }
      
      // Attach user info to request
      req.auth = { 
        type: 'jwt',
        id: decoded.id,
        role: decoded.role || 'user',
        ...decoded
      };
      next();
    } catch (err) {
      logger.warn(`JWT verification failed: ${err.message}`);
      throw new ApiError('Invalid or expired token', 401);
    }
  } catch (error) {
    next(error);
  }
};

/**
 * Combined authentication middleware that tries both API key and JWT
 * 
 * @param {Express.Request} req - Express request object
 * @param {Express.Response} res - Express response object
 * @param {Function} next - Express next middleware function
 */
const authenticate = (req, res, next) => {
  const apiKeyHeader = process.env.API_KEY_HEADER || 'X-API-Key';
  const hasApiKey = req.headers[apiKeyHeader.toLowerCase()];
  const hasAuthHeader = req.headers.authorization && req.headers.authorization.startsWith('Bearer ');

  if (hasApiKey) {
    return apiKeyAuth(req, res, next);
  } 
  
  if (hasAuthHeader) {
    return jwtAuth(req, res, next);
  }

  return next(new ApiError('Authentication required', 401));
};

/**
 * Role-based authorization middleware
 * 
 * @param {string[]} roles - Array of allowed roles
 * @returns {Function} Express middleware function
 */
const authorize = (roles = []) => {
  return (req, res, next) => {
    try {
      if (!req.auth) {
        throw new ApiError('Authentication required', 401);
      }

      // API key auth bypasses role checks for now
      if (req.auth.type === 'apiKey') {
        return next();
      }

      // Check user role
      if (roles.length && !roles.includes(req.auth.role)) {
        throw new ApiError('Insufficient permissions', 403);
      }

      next();
    } catch (error) {
      next(error);
    }
  };
};

module.exports = {
  apiKeyAuth,
  jwtAuth,
  authenticate,
  authorize,
};