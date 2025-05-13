/**
 * Database models configuration using Sequelize
 */

const { Sequelize } = require('sequelize');
const logger = require('../utils/logger');

// Load model definitions
const defineTaskModel = require('./task.model');
const defineRepositoryModel = require('./repository.model');
const defineCodeGenerationModel = require('./codeGeneration.model');
const definePullRequestModel = require('./pullRequest.model');

// Database configuration
const database = process.env.DB_NAME || 'azdevops_mcp';
const username = process.env.DB_USER || 'postgres';
const password = process.env.DB_PASSWORD || 'postgres';
const host = process.env.DB_HOST || 'localhost';
const port = process.env.DB_PORT || 5432;
const dialect = 'postgres';

// Configure SSL
const sslConfig = process.env.DB_SSL === 'true' ? {
  require: true,
  rejectUnauthorized: false,
} : false;

// Initialize Sequelize
const sequelize = new Sequelize(database, username, password, {
  host,
  port,
  dialect,
  dialectOptions: {
    ssl: sslConfig,
  },
  logging: (msg) => logger.debug(msg),
  pool: {
    max: 5,
    min: 0,
    acquire: 30000,
    idle: 10000,
  },
});

// Load all models
const models = {
  Task: defineTaskModel(sequelize),
  Repository: defineRepositoryModel(sequelize),
  CodeGeneration: defineCodeGenerationModel(sequelize),
  PullRequest: definePullRequestModel(sequelize),
};

// Set up model associations
Object.keys(models).forEach((modelName) => {
  if ('associate' in models[modelName]) {
    models[modelName].associate(models);
  }
});

// Export models and Sequelize instance
module.exports = {
  ...models,
  sequelize,
  Sequelize,
};