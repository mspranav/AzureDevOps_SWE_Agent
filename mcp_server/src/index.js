/**
 * Main entry point for the Azure DevOps Integration Agent MCP Server
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const { sequelize } = require('./models');
const logger = require('./utils/logger');
const errorHandler = require('./middleware/errorHandler');
const apiRoutes = require('./api/routes');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 3000;
const API_VERSION = process.env.API_VERSION || 'v1';

// Apply security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization', process.env.API_KEY_HEADER || 'X-API-Key'],
}));

// Rate limiting
if (process.env.ENABLE_RATE_LIMITING !== 'false') {
  const limiter = rateLimit({
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS, 10) || 60000, // 1 minute
    max: parseInt(process.env.RATE_LIMIT_MAX, 10) || 100, // 100 requests per windowMs
    standardHeaders: true,
    legacyHeaders: false,
    message: {
      status: 429,
      message: 'Too many requests, please try again later.',
    },
  });
  app.use(limiter);
}

// Request parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logging
app.use(morgan('combined', { stream: { write: (message) => logger.info(message.trim()) } }));

// API Routes
app.use(`/api/${API_VERSION}`, apiRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '0.1.0',
  });
});

// Error handling
app.use(errorHandler);

// Start the server
const startServer = async () => {
  try {
    // Initialize database connection
    await sequelize.authenticate();
    logger.info('Database connection established successfully');

    // Start listening for requests
    app.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`);
      logger.info(`API available at /api/${API_VERSION}`);
    });
  } catch (error) {
    logger.error(`Error starting server: ${error.message}`);
    process.exit(1);
  }
};

// Handle unhandled promise rejections
process.on('unhandledRejection', (error) => {
  logger.error(`Unhandled Rejection: ${error.message}`, { stack: error.stack });
  // Don't exit the process in production, but log the error
  if (process.env.NODE_ENV === 'development') {
    process.exit(1);
  }
});

// Start server if this is the main module
if (require.main === module) {
  startServer();
}

// Export for testing
module.exports = app;