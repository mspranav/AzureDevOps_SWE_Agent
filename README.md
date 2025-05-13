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
- **Containerized**: Runs in a Docker container with all necessary language SDKs and build tools

## Architecture

The agent consists of several core modules:

1. **Azure DevOps Client**: Interacts with Azure DevOps API to read tasks and create PRs
2. **Task Processor**: Interprets task requirements and orchestrates the implementation
3. **Git Handler**: Manages repository operations (clone, branch, commit)
4. **Language Detector**: Identifies programming languages and frameworks used in the repository
5. **Implementation Manager**: Orchestrates code changes across multiple files
6. **Test Runner**: Executes tests for various languages and frameworks
7. **PR Manager**: Creates properly formatted pull requests with appropriate descriptions
8. **Security Components**: Handles credentials and audit logging

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Azure DevOps organization with appropriate permissions
- Personal Access Token (PAT) with sufficient permissions

### Installation

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

### Configuration

The agent can be configured through:

- **Environment variables**: Set in `.env` file or directly in your environment
- **YAML configuration**: Edit `config/agent_config.yaml` for detailed configuration
- **Command line arguments**: Pass parameters when running the agent

#### Essential Configuration

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

## Usage

### Processing a Task

To process a specific Azure DevOps task, run:

```bash
docker exec azure-devops-agent python -m azure_devops_agent --task-id 123
```

Or configure the agent to automatically poll for tasks:

```bash
docker exec azure-devops-agent python -m azure_devops_agent --poll
```

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

## Contributing

We welcome contributions to improve the Azure DevOps Integration Agent. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Azure DevOps Python SDK
- GitPython
- Large Language Models for code generation
- The open-source tools and libraries that make this project possible