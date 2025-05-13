/**
 * Logger utility for the MCP server
 */

const winston = require('winston');
const fs = require('fs');
const path = require('path');

// Ensure log directory exists
const logDir = path.join(process.cwd(), 'logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const logLevel = process.env.LOG_LEVEL || 'info';
const logFile = process.env.LOG_FILE || 'logs/server.log';

// Define custom format
const customFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss',
  }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json(),
);

// Create a Winston logger
const logger = winston.createLogger({
  level: logLevel,
  format: customFormat,
  defaultMeta: { service: 'azdevops-mcp' },
  transports: [
    // Console transport for development
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.printf(
          (info) => `${info.timestamp} ${info.level}: ${info.message}`,
        ),
      ),
    }),

    // File transport for production
    new winston.transports.File({
      filename: logFile,
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true,
    }),

    // Error specific transport
    new winston.transports.File({
      filename: 'logs/error.log',
      level: 'error',
      maxsize: 5242880, // 5MB
      maxFiles: 5,
      tailable: true,
    }),
  ],
});

// Add stream for Morgan middleware
logger.stream = {
  write: (message) => {
    logger.info(message.trim());
  },
};

// Export the logger
module.exports = logger;