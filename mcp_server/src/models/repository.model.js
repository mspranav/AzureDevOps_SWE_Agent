/**
 * Repository model definition
 */

const { DataTypes } = require('sequelize');

/**
 * Define Repository model 
 * 
 * @param {Sequelize} sequelize - Sequelize instance
 * @returns {SequelizeModel} Repository model
 */
module.exports = (sequelize) => {
  const Repository = sequelize.define('Repository', {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true,
    },
    url: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Repository URL',
    },
    name: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Repository name',
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
    repositoryId: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Repository ID in Azure DevOps',
    },
    defaultBranch: {
      type: DataTypes.STRING,
      defaultValue: 'main',
      comment: 'Default branch name',
    },
    analysis: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Repository analysis results',
    },
    languages: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Detected languages and their percentages',
    },
    frameworks: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Detected frameworks',
    },
    codeStyle: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Detected code style preferences',
    },
    lastAnalyzedAt: {
      type: DataTypes.DATE,
      comment: 'When the repository was last analyzed',
    },
    lastClonedAt: {
      type: DataTypes.DATE,
      comment: 'When the repository was last cloned',
    },
    metadata: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Additional metadata for the repository',
    },
  }, {
    tableName: 'repositories',
    timestamps: true,
    indexes: [
      {
        unique: true,
        fields: ['url'],
      },
      {
        unique: true,
        fields: ['organization', 'project', 'repositoryId'],
      },
    ],
  });

  Repository.associate = (models) => {
    Repository.hasMany(models.Task, {
      foreignKey: 'repositoryId',
      as: 'tasks',
    });
    
    Repository.hasMany(models.PullRequest, {
      foreignKey: 'repositoryId',
      as: 'pullRequests',
    });
  };

  return Repository;
};