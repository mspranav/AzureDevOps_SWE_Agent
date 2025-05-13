/**
 * PullRequest model definition
 */

const { DataTypes } = require('sequelize');

/**
 * Define PullRequest model 
 * 
 * @param {Sequelize} sequelize - Sequelize instance
 * @returns {SequelizeModel} PullRequest model
 */
module.exports = (sequelize) => {
  const PullRequest = sequelize.define('PullRequest', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    taskId: {
      type: DataTypes.UUID,
      allowNull: false,
      comment: 'ID of the associated task',
    },
    repositoryId: {
      type: DataTypes.UUID,
      allowNull: false,
      comment: 'ID of the associated repository',
    },
    pullRequestId: {
      type: DataTypes.STRING,
      comment: 'Pull request ID in Azure DevOps',
    },
    title: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Pull request title',
    },
    description: {
      type: DataTypes.TEXT,
      comment: 'Pull request description',
    },
    sourceBranch: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Source branch name',
    },
    targetBranch: {
      type: DataTypes.STRING,
      allowNull: false,
      defaultValue: 'main',
      comment: 'Target branch name',
    },
    status: {
      type: DataTypes.ENUM('draft', 'open', 'merged', 'closed'),
      defaultValue: 'draft',
      allowNull: false,
      comment: 'Current status of the pull request',
    },
    url: {
      type: DataTypes.STRING,
      comment: 'URL to the pull request',
    },
    changedFiles: {
      type: DataTypes.JSONB,
      defaultValue: [],
      comment: 'List of files changed in the PR',
    },
    reviewers: {
      type: DataTypes.JSONB,
      defaultValue: [],
      comment: 'List of PR reviewers',
    },
    createdInAzureDevOps: {
      type: DataTypes.BOOLEAN,
      defaultValue: false,
      comment: 'Whether the PR was created in Azure DevOps',
    },
    createdInAzureDevOpsAt: {
      type: DataTypes.DATE,
      comment: 'When the PR was created in Azure DevOps',
    },
    mergedAt: {
      type: DataTypes.DATE,
      comment: 'When the PR was merged',
    },
    closedAt: {
      type: DataTypes.DATE,
      comment: 'When the PR was closed',
    },
    metrics: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'PR metrics (size, time to merge, etc.)',
    },
    metadata: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Additional metadata for the PR',
    },
  }, {
    tableName: 'pull_requests',
    timestamps: true,
    indexes: [
      {
        fields: ['taskId'],
      },
      {
        fields: ['repositoryId'],
      },
      {
        fields: ['pullRequestId'],
      },
      {
        fields: ['status'],
      },
    ],
  });

  PullRequest.associate = (models) => {
    PullRequest.belongsTo(models.Task, {
      foreignKey: 'taskId',
      as: 'task',
    });
    
    PullRequest.belongsTo(models.Repository, {
      foreignKey: 'repositoryId',
      as: 'repository',
    });
  };

  return PullRequest;
};