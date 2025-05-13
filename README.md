# Azure DevOps Integration Agent

An AI-powered agent that automates Azure DevOps tasks by implementing code changes, running tests, and creating pull requests across multiple programming languages.

## Overview

The Azure DevOps Integration Agent is designed to reduce developer workload by autonomously handling routine tasks in Azure DevOps. It reads task details, analyzes repositories, implements required changes in the appropriate programming language, runs tests to verify the implementation, and creates properly formatted pull requests.

### Key Features

- **Multi-language Support**: Works with JavaScript/TypeScript, Python, Java, C#, Go, Ruby, PHP, Rust, Swift, and C/C++
- **Framework Detection**: Automatically detects and adapts to popular frameworks within each language ecosystem
- **Code Style Matching**: Implements changes that match the existing code style and patterns
- **Comprehensive Testing**: Runs existing tests and generates new tests as needed
- **Security-focused**: Includes secure credential management and audit logging
- **Deployment Options**: 
  - Docker container with all necessary language SDKs and build tools
  - MCP (Model Completion Provider) server architecture for cloud-based deployment

## Architecture Options

The agent offers two deployment architectures:

### 1. Containerized Agent (Original Implementation)

The containerized implementation runs the agent in a Docker container with all necessary language SDKs and build tools installed. This approach is self-contained and can be run on any system with Docker support.

Components:
1. **Azure DevOps Client**: Interacts with Azure DevOps API to read tasks and create PRs
2. **Task Processor**: Interprets task requirements and orchestrates the implementation
3. **Git Handler**: Manages repository operations (clone, branch, commit)
4. **Language Detector**: Identifies programming languages and frameworks used in the repository
5. **Implementation Manager**: Orchestrates code changes across multiple files
6. **Test Runner**: Executes tests for various languages and frameworks
7. **PR Manager**: Creates properly formatted pull requests with appropriate descriptions
8. **Security Components**: Handles credentials and audit logging

### 2. MCP Server (Cloud Implementation)

The MCP server implementation provides a scalable, cloud-based architecture with a RESTful API for better performance and simplified deployment. This approach eliminates the need to install language SDKs locally and can handle multiple concurrent tasks efficiently.

Components:
1. **API Server**: FastAPI-based REST API with authentication and rate limiting
2. **Task Processing Service**: Handles Azure DevOps task interpretation and orchestration
3. **Language Service**: Performs language detection and code style analysis
4. **Code Generation Service**: Generates code implementations across languages
5. **Repository Service**: Manages Git operations
6. **PR Service**: Creates and manages pull requests
7. **Security Service**: Handles credentials and audit logging

The MCP server is available in both Node.js (Express) and Python (FastAPI) implementations.

## Getting Started

### Prerequisites

For Containerized Agent:
- Docker and Docker Compose
- Azure DevOps organization with appropriate permissions
- Personal Access Token (PAT) with sufficient permissions

For MCP Server:
- Node.js 18+ or Python 3.9+ (depending on implementation choice)
- PostgreSQL database (or SQLite for development)
- Redis (optional, for caching)
- Azure DevOps organization with appropriate permissions
- Personal Access Token (PAT) with sufficient permissions

### Installation

#### Containerized Agent

1. Clone this repository:
   ```
   git clone https://github.com/your-org/azure-devops-agent.git
   cd azure-devops-agent
   ```

2. Create configuration files:
   ```
   cp .env.example .env
   cp config/agent_config.yaml.example config/agent_config.yaml
   ```

3. Update the configuration files with your Azure DevOps details and preferences

4. Build and start the container:
   ```
   docker-compose up -d
   ```

#### MCP Server - Node.js

1. Navigate to the MCP server directory:
   ```
   cd azure-devops-agent/mcp_server
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create configuration:
   ```
   cp .env.example .env
   ```

4. Update the .env file with your database, Azure DevOps, and other settings

5. Start the server:
   ```
   npm start
   ```

#### MCP Server - Python

1. Navigate to the MCP server directory:
   ```
   cd azure-devops-agent/mcp_server_python
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create configuration:
   ```
   cp .env.example .env
   ```

5. Update the .env file with your database, Azure DevOps, and other settings

6. Initialize the database:
   ```
   python create_db_migration.py
   ```

7. Start the server:
   ```
   uvicorn app.main:app --reload
   ```

### Configuration

#### Containerized Agent

The agent can be configured through:

- **Environment variables**: Set in `.env` file or directly in your environment
- **YAML configuration**: Edit `config/agent_config.yaml` for detailed configuration
- **Command line arguments**: Pass parameters when running the agent

```yaml
# in config/agent_config.yaml
azure_devops:
  organization: "your-organization"
  project: "your-project"
  # Token should be set via AZURE_DEVOPS_PAT environment variable

repository:
  work_dir: "/app/repos"
  default_branch: "main"

security:
  credential_store: "env"
  audit_log: "/app/logs/audit.log"
```

```
# in .env
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORG=your_organization
AZURE_DEVOPS_PROJECT=your_project
```

#### MCP Server

The MCP server is configured through environment variables:

```
# Server configuration
PORT=8000
DEBUG=True
API_VERSION=v1

# Security
SECRET_KEY=your_secret_key_here
VALID_API_KEYS=dev-api-key,test-api-key

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# Azure DevOps
AZURE_DEVOPS_PAT=your_personal_access_token
AZURE_DEVOPS_ORGANIZATION=your_organization

# OpenAI (for code generation)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
```

## Usage

### Containerized Agent

To process a specific Azure DevOps task, run:

```bash
docker exec azure-devops-agent python -m azure_devops_agent --task-id 123
```

Or configure the agent to automatically poll for tasks:

```bash
docker exec azure-devops-agent python -m azure_devops_agent --poll
```

### MCP Server API

The MCP server provides a RESTful API:

```bash
# Create a new task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "azure_devops_id": "123",
    "organization": "your-organization",
    "project": "your-project",
    "title": "Implement feature X",
    "description": "Add new functionality for feature X",
    "requirements": {
      "files_to_modify": ["src/feature.js"],
      "testing_required": true
    }
  }'

# Get task status
curl -X GET http://localhost:8000/api/v1/tasks/task-uuid \
  -H "X-API-Key: your-api-key"
```

Python MCP server also provides interactive API documentation at `/docs` when running in development mode.

### Task Assignment

To have the agent work on a task, assign it to the agent in Azure DevOps:

1. Create or edit a work item in Azure DevOps
2. Assign it to the user account the agent is configured to use
3. Include clear requirements in the description
4. The agent will process the task, implement the changes, and create a PR

### Pull Request Format

The agent creates PRs with the following format:

```
Title: [Task #{task_number}] {Brief description} (AI Agent)

Description:
## Summary
{Brief description of changes implemented}

## Implemented Changes
- {Detailed list of changes made}
- {Code areas affected}
- {New functionality added}

## Testing
- {Tests executed}
- {Test results}
- {Any fixed issues}

## Task Reference
This PR addresses Azure DevOps Task #{task_number}

_This pull request was created by an AI Agent_
```

## Use Cases

### 1. Standard Task Completion

The agent can handle routine implementation tasks like:

- Adding new API endpoints
- Implementing simple features
- Creating CRUD operations
- Updating configuration
- Refactoring code
- Adding tests

### 2. Complex Tasks with Clarification

If the task requirements are incomplete or ambiguous:

1. The agent will add a comment requesting clarification
2. After you provide the additional information, the agent will proceed with implementation

### 3. Tasks with Build Issues

If the agent encounters build or test failures:

1. It will diagnose the issues
2. Attempt to fix the problems
3. Document the resolution in the PR description

## Advanced Features

### Cross-Repository Dependencies

The agent can detect when changes span multiple repositories and will note these dependencies in the PR description.

### Performance Optimization Tasks

For performance-focused tasks, the agent can run benchmarks before and after changes, including the comparison in the PR.

### Feature Flag Implementation

When implementing features that require feature flags, the agent will:

1. Implement code with appropriate feature flag controls
2. Test both enabled and disabled states
3. Document feature flag configuration in the PR

## Security

The agent includes several security features:

- **Credential Management**: Secure storage of tokens and credentials
- **Audit Logging**: Detailed logs of all agent actions
- **Limited Access Scope**: Access only to assigned repositories
- **Secure Credential Storage**: Options for keyring, environment variables, or Azure identity
- **API Authentication**: API key and JWT authentication for MCP server

## API Reference (MCP Server)

### Tasks
- `POST /api/v1/tasks`: Create a new task
- `GET /api/v1/tasks`: List all tasks
- `GET /api/v1/tasks/{id}`: Get task details
- `PATCH /api/v1/tasks/{id}`: Update task status
- `DELETE /api/v1/tasks/{id}`: Delete a task

### Repositories
- `GET /api/v1/repositories`: List repositories
- `GET /api/v1/repositories/{id}`: Get repository details

### Code Generation
- `GET /api/v1/code/generations/{id}`: Get code generation details
- `GET /api/v1/code/tasks/{id}/generations`: Get all code generations for a task

### Pull Requests
- `GET /api/v1/prs`: List pull requests
- `GET /api/v1/prs/{id}`: Get pull request details
- `GET /api/v1/prs/tasks/{id}`: Get pull request for a task

## Contributing

We welcome contributions to improve the Azure DevOps Integration Agent. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Azure DevOps Python/JavaScript SDK
- GitPython
- FastAPI/Express
- SQLAlchemy/Sequelize
- Large Language Models for code generation
- The open-source tools and libraries that make this project possible