/**
 * Task model definition
 */

const { DataTypes } = require('sequelize');

/**
 * Define Task model 
 * 
 * @param {Sequelize} sequelize - Sequelize instance
 * @returns {SequelizeModel} Task model
 */
module.exports = (sequelize) => {
  const Task = sequelize.define('Task', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    azureDevOpsId: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'ID of the task in Azure DevOps',
    },
    organization: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Azure DevOps organization',
    },
    project: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Azure DevOps project',
    },
    title: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Task title',
    },
    description: {
      type: DataTypes.TEXT,
      comment: 'Task description',
    },
    status: {
      type: DataTypes.ENUM('pending', 'in_progress', 'completed', 'failed', 'cancelled'),
      defaultValue: 'pending',
      allowNull: false,
      comment: 'Current status of the task',
    },
    requirements: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'JSON object with task requirements',
    },
    analysis: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'JSON object with task analysis results',
    },
    result: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'JSON object with task processing results',
    },
    startedAt: {
      type: DataTypes.DATE,
      comment: 'When task processing started',
    },
    completedAt: {
      type: DataTypes.DATE,
      comment: 'When task processing completed',
    },
    error: {
      type: DataTypes.TEXT,
      comment: 'Error message if task failed',
    },
    priority: {
      type: DataTypes.INTEGER,
      defaultValue: 0,
      comment: 'Task priority (higher number = higher priority)',
    },
    metadata: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Additional metadata for the task',
    },
  }, {
    tableName: 'tasks',
    timestamps: true,
    paranoid: true, // Soft delete
    indexes: [
      {
        unique: true,
        fields: ['azureDevOpsId'],
      },
      {
        fields: ['status'],
      },
      {
        fields: ['organization', 'project'],
      },
    ],
  });

  Task.associate = (models) => {
    Task.hasMany(models.CodeGeneration, {
      foreignKey: 'taskId',
      as: 'codeGenerations',
    });
    
    Task.hasOne(models.PullRequest, {
      foreignKey: 'taskId',
      as: 'pullRequest',
    });
    
    Task.belongsTo(models.Repository, {
      foreignKey: 'repositoryId',
      as: 'repository',
    });
  };

  return Task;
};