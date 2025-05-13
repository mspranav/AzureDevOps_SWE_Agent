# Contributing to Azure DevOps Integration Agent

We love your input! We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Requests

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Pull Request Guidelines

- Update the README.md with details of changes if applicable
- Update the documentation with details of any API changes
- The PR should work for all supported languages and environments
- Ensure all tests pass

## Development Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install development dependencies: `pip install -e ".[dev]"`
5. Configure pre-commit hooks: `pre-commit install`

## Testing

Run tests using pytest:

```bash
pytest
```

For coverage report:

```bash
pytest --cov=azure_devops_agent
```

## Code Style

This project uses:
- Black for Python code formatting
- isort for import sorting
- flake8 for linting

You can run all style checks with:

```bash
pre-commit run --all-files
```

## Adding Support for New Languages

To add support for a new programming language:

1. Update the `LANGUAGE_EXTENSIONS` dictionary in `azure_devops_agent/implementation/language_detector.py`
2. Add language-specific patterns in `FRAMEWORK_PATTERNS`
3. Implement a language-specific code generator in `azure_devops_agent/implementation/code_generator.py`
4. Add test command templates in `azure_devops_agent/testing/test_runner.py`
5. Update the Dockerfile to include the language's SDK and build tools
6. Add tests for the new language support

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.