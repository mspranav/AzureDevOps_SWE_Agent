/**
 * CodeGeneration model definition
 */

const { DataTypes } = require('sequelize');

/**
 * Define CodeGeneration model 
 * 
 * @param {Sequelize} sequelize - Sequelize instance
 * @returns {SequelizeModel} CodeGeneration model
 */
module.exports = (sequelize) => {
  const CodeGeneration = sequelize.define('CodeGeneration', {
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
    language: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Programming language',
    },
    framework: {
      type: DataTypes.STRING,
      comment: 'Framework used',
    },
    filePath: {
      type: DataTypes.STRING,
      allowNull: false,
      comment: 'Path to the file being generated/modified',
    },
    action: {
      type: DataTypes.ENUM('create', 'modify', 'delete'),
      allowNull: false,
      defaultValue: 'create',
      comment: 'Action being performed on the file',
    },
    requirements: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Requirements for code generation',
    },
    originalCode: {
      type: DataTypes.TEXT,
      comment: 'Original code before modification (for modify action)',
    },
    generatedCode: {
      type: DataTypes.TEXT,
      comment: 'Generated code implementation',
    },
    testCode: {
      type: DataTypes.TEXT,
      comment: 'Generated test code (if applicable)',
    },
    prompt: {
      type: DataTypes.TEXT,
      comment: 'Prompt used for code generation',
    },
    modelName: {
      type: DataTypes.STRING,
      comment: 'AI model name used for generation',
    },
    modelVersion: {
      type: DataTypes.STRING,
      comment: 'AI model version used for generation',
    },
    status: {
      type: DataTypes.ENUM('pending', 'in_progress', 'completed', 'failed'),
      defaultValue: 'pending',
      allowNull: false,
      comment: 'Status of code generation',
    },
    error: {
      type: DataTypes.TEXT,
      comment: 'Error message if code generation failed',
    },
    metrics: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Generation metrics (tokens, time, etc.)',
    },
    metadata: {
      type: DataTypes.JSONB,
      defaultValue: {},
      comment: 'Additional metadata for code generation',
    },
  }, {
    tableName: 'code_generations',
    timestamps: true,
    indexes: [
      {
        fields: ['taskId'],
      },
      {
        fields: ['language'],
      },
      {
        fields: ['status'],
      },
    ],
  });

  CodeGeneration.associate = (models) => {
    CodeGeneration.belongsTo(models.Task, {
      foreignKey: 'taskId',
      as: 'task',
    });
  };

  return CodeGeneration;
};