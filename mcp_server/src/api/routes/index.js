/**
 * Main API routes configuration
 */

const express = require('express');
const { authenticate } = require('../../middleware/auth');
const taskRoutes = require('./task.routes');
const repositoryRoutes = require('./repository.routes');
const codeGenerationRoutes = require('./codeGeneration.routes');
const pullRequestRoutes = require('./pullRequest.routes');

const router = express.Router();

// Base route
router.get('/', (req, res) => {
  res.json({
    message: 'Azure DevOps Integration Agent MCP API',
    version: process.env.npm_package_version || '0.1.0',
    endpoints: [
      '/tasks',
      '/repositories',
      '/code',
      '/prs',
    ],
  });
});

// Apply authentication middleware to all routes
// Can be disabled in development by setting DISABLE_AUTH=true
if (process.env.DISABLE_AUTH !== 'true') {
  router.use(authenticate);
}

// Mount feature routes
router.use('/tasks', taskRoutes);
router.use('/repositories', repositoryRoutes);
router.use('/code', codeGenerationRoutes);
router.use('/prs', pullRequestRoutes);

module.exports = router;