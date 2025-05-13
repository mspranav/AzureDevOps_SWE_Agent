"""
Test Runner module for Azure DevOps Integration Agent.

This module provides functionality to execute tests across multiple programming
languages and frameworks, detecting the appropriate test commands to run.
"""

import os
import logging
import subprocess
import json
import re
from typing import Dict, List, Optional, Any, Tuple, Union

logger = logging.getLogger(__name__)

class TestRunner:
    """Run tests for multiple programming languages and frameworks."""
    
    # Language-specific test commands
    TEST_COMMANDS = {
        'JavaScript': {
            'Jest': 'npx jest {path} --no-cache',
            'Mocha': 'npx mocha {path}',
            'Jasmine': 'npx jasmine {path}',
            'default': 'npm test'
        },
        'TypeScript': {
            'Jest': 'npx jest {path} --no-cache',
            'Mocha': 'npx mocha -r ts-node/register {path}',
            'default': 'npm test'
        },
        'Python': {
            'pytest': 'python -m pytest {path} -v',
            'unittest': 'python -m unittest {path}',
            'nose': 'nosetests {path}',
            'default': 'python -m pytest {path}'
        },
        'Java': {
            'JUnit': './gradlew test --tests {class_name}',
            'TestNG': './gradlew test --tests {class_name}',
            'Maven': 'mvn test -Dtest={class_name}',
            'default': './gradlew test'
        },
        'Kotlin': {
            'JUnit': './gradlew test --tests {class_name}',
            'default': './gradlew test'
        },
        'C#': {
            'NUnit': 'dotnet test {path} --filter {class_name}',
            'xUnit': 'dotnet test {path} --filter {class_name}',
            'MSTest': 'dotnet test {path} --filter {class_name}',
            'default': 'dotnet test {path}'
        },
        'Go': {
            'default': 'go test {package_path}'
        },
        'Ruby': {
            'RSpec': 'bundle exec rspec {path}',
            'default': 'bundle exec rake test'
        },
        'PHP': {
            'PHPUnit': './vendor/bin/phpunit {path}',
            'default': './vendor/bin/phpunit'
        },
        'Rust': {
            'default': 'cargo test {test_name}'
        },
        'Swift': {
            'default': 'swift test --filter {test_name}'
        }
    }
    
    # Test file patterns by language
    TEST_FILE_PATTERNS = {
        'JavaScript': [
            r'.*\.test\.js$',
            r'.*\.spec\.js$',
            r'__tests__/.*\.js$'
        ],
        'TypeScript': [
            r'.*\.test\.ts$',
            r'.*\.spec\.ts$',
            r'__tests__/.*\.ts$'
        ],
        'Python': [
            r'test_.*\.py$',
            r'.*_test\.py$',
            r'tests/.*\.py$'
        ],
        'Java': [
            r'.*Test\.java$',
            r'Test.*\.java$'
        ],
        'Kotlin': [
            r'.*Test\.kt$',
            r'Test.*\.kt$'
        ],
        'C#': [
            r'.*Tests?\.cs$',
            r'Tests?.*\.cs$'
        ],
        'Go': [
            r'.*_test\.go$'
        ],
        'Ruby': [
            r'.*_spec\.rb$',
            r'spec/.*\.rb$'
        ],
        'PHP': [
            r'.*Test\.php$',
            r'Test.*\.php$'
        ],
        'Rust': [
            r'.*\.rs$'  # Tests in Rust are usually defined within the same file
        ],
        'Swift': [
            r'.*Tests?\.swift$',
            r'Tests?.*\.swift$'
        ]
    }
    
    # Build tool detection patterns by language
    BUILD_TOOLS = {
        'JavaScript': {
            'npm': 'package.json',
            'yarn': 'yarn.lock',
            'pnpm': 'pnpm-lock.yaml'
        },
        'TypeScript': {
            'npm': 'package.json',
            'yarn': 'yarn.lock',
            'pnpm': 'pnpm-lock.yaml'
        },
        'Python': {
            'pip': 'requirements.txt',
            'pipenv': 'Pipfile',
            'poetry': 'pyproject.toml'
        },
        'Java': {
            'gradle': 'build.gradle',
            'maven': 'pom.xml'
        },
        'Kotlin': {
            'gradle': 'build.gradle.kts',
            'maven': 'pom.xml'
        },
        'C#': {
            'dotnet': '.csproj'
        },
        'Go': {
            'go': 'go.mod'
        },
        'Ruby': {
            'bundler': 'Gemfile'
        },
        'PHP': {
            'composer': 'composer.json'
        },
        'Rust': {
            'cargo': 'Cargo.toml'
        },
        'Swift': {
            'swift': 'Package.swift'
        }
    }
    
    def __init__(self, repo_path: str):
        """
        Initialize the test runner.
        
        Args:
            repo_path: Path to the repository root directory.
        """
        self.repo_path = repo_path
        logger.info(f"Test runner initialized for repository at {repo_path}")
    
    def run_tests(self, 
                 language: str, 
                 test_file_path: Optional[str] = None,
                 test_class: Optional[str] = None,
                 test_framework: Optional[str] = None) -> Dict[str, Any]:
        """
        Run tests for a specific language and test file.
        
        Args:
            language: Programming language.
            test_file_path: Path to the test file (optional).
            test_class: Name of the test class to run (optional).
            test_framework: Name of the test framework to use (optional).
            
        Returns:
            Dictionary with test results.
        """
        # Detect the test framework if not specified
        if not test_framework:
            test_framework = self._detect_test_framework(language)
            logger.info(f"Detected test framework: {test_framework}")
        
        # Find test files if not specified
        if not test_file_path:
            test_files = self._find_test_files(language)
            logger.info(f"Found {len(test_files)} test files for {language}")
            
            if not test_files:
                return {
                    'status': 'error',
                    'message': f"No test files found for {language}",
                    'tests_run': 0,
                    'tests_passed': 0,
                    'tests_failed': 0
                }
                
            # Run all tests if no specific file is provided
            results = []
            for test_file in test_files:
                result = self._execute_test_command(language, test_framework, test_file, test_class)
                results.append(result)
                
            # Aggregate results
            return self._aggregate_test_results(results)
        else:
            # Run tests for the specified file
            result = self._execute_test_command(language, test_framework, test_file_path, test_class)
            return result
    
    def _detect_test_framework(self, language: str) -> str:
        """
        Detect the test framework used in the repository for a language.
        
        Args:
            language: Programming language.
            
        Returns:
            Name of the detected test framework, or 'default' if not detected.
        """
        # Check for language-specific build/package files
        if language in self.BUILD_TOOLS:
            for build_tool, file_pattern in self.BUILD_TOOLS[language].items():
                for root, _, files in os.walk(self.repo_path):
                    for file in files:
                        if file == file_pattern or file.endswith(file_pattern):
                            # Found a build file, now look for test framework dependencies
                            file_path = os.path.join(root, file)
                            
                            # Parse the file based on its type
                            if file.endswith('.json'):  # package.json, composer.json
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        data = json.load(f)
                                        
                                    # Check dependencies
                                    deps = {}
                                    if 'dependencies' in data:
                                        deps.update(data['dependencies'])
                                    if 'devDependencies' in data:
                                        deps.update(data['devDependencies'])
                                        
                                    # Check for test frameworks
                                    if language in ['JavaScript', 'TypeScript']:
                                        if 'jest' in deps:
                                            return 'Jest'
                                        elif 'mocha' in deps:
                                            return 'Mocha'
                                        elif 'jasmine' in deps:
                                            return 'Jasmine'
                                    elif language == 'PHP':
                                        if 'phpunit/phpunit' in deps:
                                            return 'PHPUnit'
                                except Exception as e:
                                    logger.warning(f"Error parsing {file_path}: {str(e)}")
                            
                            elif file.endswith('.txt') or file == 'Pipfile':  # requirements.txt, Pipfile
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        
                                    if language == 'Python':
                                        if 'pytest' in content:
                                            return 'pytest'
                                        elif 'unittest' in content:
                                            return 'unittest'
                                        elif 'nose' in content:
                                            return 'nose'
                                except Exception as e:
                                    logger.warning(f"Error reading {file_path}: {str(e)}")
                            
                            elif file.endswith('.toml'):  # pyproject.toml, Cargo.toml
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        
                                    if language == 'Python':
                                        if 'pytest' in content:
                                            return 'pytest'
                                except Exception as e:
                                    logger.warning(f"Error reading {file_path}: {str(e)}")
                            
                            elif file.endswith('.xml'):  # pom.xml
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        
                                    if language in ['Java', 'Kotlin']:
                                        if 'junit' in content.lower():
                                            return 'JUnit'
                                        elif 'testng' in content.lower():
                                            return 'TestNG'
                                except Exception as e:
                                    logger.warning(f"Error reading {file_path}: {str(e)}")
                            
                            elif file.endswith('.gradle') or file.endswith('.gradle.kts'):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        
                                    if language in ['Java', 'Kotlin']:
                                        if 'junit' in content.lower():
                                            return 'JUnit'
                                        elif 'testng' in content.lower():
                                            return 'TestNG'
                                except Exception as e:
                                    logger.warning(f"Error reading {file_path}: {str(e)}")
                            
                            elif file.endswith('.csproj') or file.endswith('.sln'):
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        content = f.read()
                                        
                                    if language == 'C#':
                                        if 'nunit' in content.lower():
                                            return 'NUnit'
                                        elif 'xunit' in content.lower():
                                            return 'xUnit'
                                        elif 'mstest' in content.lower():
                                            return 'MSTest'
                                except Exception as e:
                                    logger.warning(f"Error reading {file_path}: {str(e)}")
        
        # If no framework detected, check test files for framework-specific patterns
        test_files = self._find_test_files(language)
        for test_file in test_files[:5]:  # Check up to 5 files
            try:
                with open(os.path.join(self.repo_path, test_file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                if language in ['JavaScript', 'TypeScript']:
                    if 'jest' in content.lower() or 'describe(' in content or 'test(' in content or 'it(' in content:
                        return 'Jest'
                    elif 'mocha' in content.lower():
                        return 'Mocha'
                    elif 'jasmine' in content.lower():
                        return 'Jasmine'
                elif language == 'Python':
                    if 'pytest' in content.lower() or '@pytest' in content:
                        return 'pytest'
                    elif 'unittest' in content:
                        return 'unittest'
                    elif 'nose' in content:
                        return 'nose'
                elif language in ['Java', 'Kotlin']:
                    if 'org.junit' in content:
                        return 'JUnit'
                    elif 'org.testng' in content:
                        return 'TestNG'
                elif language == 'C#':
                    if 'NUnit' in content:
                        return 'NUnit'
                    elif 'Xunit' in content:
                        return 'xUnit'
                    elif 'Microsoft.VisualStudio.TestTools' in content:
                        return 'MSTest'
                elif language == 'Ruby':
                    if 'RSpec' in content:
                        return 'RSpec'
                elif language == 'PHP':
                    if 'PHPUnit' in content:
                        return 'PHPUnit'
            except Exception as e:
                logger.warning(f"Error analyzing test file {test_file}: {str(e)}")
        
        # Default to the default framework for the language
        logger.info(f"No specific test framework detected for {language}, using default")
        return 'default'
    
    def _find_test_files(self, language: str) -> List[str]:
        """
        Find test files for a specific language in the repository.
        
        Args:
            language: Programming language.
            
        Returns:
            List of paths to test files.
        """
        test_files = []
        
        if language not in self.TEST_FILE_PATTERNS:
            logger.warning(f"No test file patterns defined for {language}")
            return test_files
            
        patterns = self.TEST_FILE_PATTERNS[language]
        compiled_patterns = [re.compile(pattern) for pattern in patterns]
        
        for root, _, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in root.split(os.path.sep):
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.repo_path)
                
                # Check if file matches any test pattern
                if any(pattern.match(file) for pattern in compiled_patterns):
                    test_files.append(rel_path)
                    
                # Additional check for Rust, which has tests inside regular files
                elif language == 'Rust' and file.endswith('.rs'):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for Rust test module
                        if '#[cfg(test)]' in content or '#[test]' in content:
                            test_files.append(rel_path)
                    except Exception as e:
                        logger.warning(f"Error checking Rust file {file_path}: {str(e)}")
        
        return test_files
    
    def _execute_test_command(self, 
                           language: str, 
                           framework: str, 
                           test_path: str,
                           test_class: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a test command for a specific language, framework, and test file.
        
        Args:
            language: Programming language.
            framework: Test framework.
            test_path: Path to the test file.
            test_class: Name of the test class (optional).
            
        Returns:
            Dictionary with test execution results.
        """
        if language not in self.TEST_COMMANDS:
            return {
                'status': 'error',
                'message': f"Unsupported language: {language}",
                'command': None,
                'output': None,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
            
        # Get the command template for the language and framework
        command_templates = self.TEST_COMMANDS[language]
        command_template = command_templates.get(framework, command_templates['default'])
        
        # Prepare command parameters
        params = {
            'path': test_path
        }
        
        # Special handling for languages that need additional parameters
        if language in ['Java', 'Kotlin', 'C#'] and test_class:
            # For Java/Kotlin/C#, we might need the class name
            params['class_name'] = test_class
        elif language == 'Go':
            # For Go, we need the package path
            package_path = os.path.dirname(test_path).replace(os.path.sep, '/')
            if not package_path:
                package_path = '.'
            params['package_path'] = package_path
        elif language in ['Rust', 'Swift'] and test_class:
            # For Rust and Swift, we might need the test name
            params['test_name'] = test_class
            
        # Format the command with parameters
        command = command_template.format(**params)
        
        try:
            # Execute the command
            logger.info(f"Executing test command: {command}")
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=self.repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate(timeout=300)  # 5-minute timeout
            exit_code = process.returncode
            
            # Parse test results
            result = self._parse_test_results(language, framework, stdout, stderr, exit_code)
            result['command'] = command
            result['test_path'] = test_path
            
            logger.info(f"Test execution completed with status: {result['status']}")
            return result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Test execution timed out: {command}")
            process.kill()
            
            return {
                'status': 'timeout',
                'message': "Test execution timed out",
                'command': command,
                'output': None,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
            
        except Exception as e:
            logger.error(f"Error executing test command: {str(e)}")
            
            return {
                'status': 'error',
                'message': f"Error executing test command: {str(e)}",
                'command': command,
                'output': None,
                'tests_run': 0,
                'tests_passed': 0,
                'tests_failed': 0
            }
    
    def _parse_test_results(self, 
                          language: str, 
                          framework: str, 
                          stdout: str, 
                          stderr: str, 
                          exit_code: int) -> Dict[str, Any]:
        """
        Parse test execution results.
        
        Args:
            language: Programming language.
            framework: Test framework.
            stdout: Standard output from test execution.
            stderr: Standard error from test execution.
            exit_code: Exit code from test execution.
            
        Returns:
            Dictionary with parsed test results.
        """
        output = stdout + "\n" + stderr
        
        # Initialize result with default values
        result = {
            'status': 'passed' if exit_code == 0 else 'failed',
            'output': output,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'failures': []
        }
        
        # Language and framework specific result parsing
        if language in ['JavaScript', 'TypeScript'] and framework == 'Jest':
            # Parse Jest output
            try:
                # Look for test summary
                summary_match = re.search(r'Tests:\s+(\d+)\s+failed,\s+(\d+)\s+passed,\s+(\d+)\s+total', output)
                if summary_match:
                    result['tests_failed'] = int(summary_match.group(1))
                    result['tests_passed'] = int(summary_match.group(2))
                    result['tests_run'] = int(summary_match.group(3))
                    
                # Extract failure information
                failures = []
                for failure_match in re.finditer(r'● (.*?)\n', output):
                    failures.append(failure_match.group(1))
                    
                result['failures'] = failures
            except Exception as e:
                logger.warning(f"Error parsing Jest test results: {str(e)}")
                
        elif language == 'Python' and framework == 'pytest':
            # Parse pytest output
            try:
                # Look for test summary
                summary_match = re.search(r'(\d+) passed,?\s*(\d+) failed,?\s*(\d+) skipped', output)
                if summary_match:
                    result['tests_passed'] = int(summary_match.group(1))
                    result['tests_failed'] = int(summary_match.group(2))
                    result['tests_skipped'] = int(summary_match.group(3))
                    result['tests_run'] = result['tests_passed'] + result['tests_failed'] + result['tests_skipped']
                    
                # Extract failure information
                failures = []
                in_failure_section = False
                for line in output.split('\n'):
                    if line.startswith('FAILED '):
                        in_failure_section = True
                        failures.append(line[7:])
                    elif in_failure_section and line.startswith('_'):
                        in_failure_section = False
                        
                result['failures'] = failures
            except Exception as e:
                logger.warning(f"Error parsing pytest test results: {str(e)}")
                
        elif language in ['Java', 'Kotlin']:
            # Parse JUnit/Gradle output
            try:
                # Look for test summary
                summary_match = re.search(r'(\d+) tests? completed, (\d+) failed', output)
                if summary_match:
                    total = int(summary_match.group(1))
                    failed = int(summary_match.group(2))
                    result['tests_run'] = total
                    result['tests_failed'] = failed
                    result['tests_passed'] = total - failed
                    
                # Extract failure information
                failures = []
                for line in output.split('\n'):
                    if 'Test FAILED' in line:
                        failures.append(line.strip())
                        
                result['failures'] = failures
            except Exception as e:
                logger.warning(f"Error parsing JUnit test results: {str(e)}")
                
        elif language == 'C#':
            # Parse dotnet test output
            try:
                # Look for test summary
                summary_match = re.search(r'Total tests: (\d+). Passed: (\d+). Failed: (\d+). Skipped: (\d+)', output)
                if summary_match:
                    result['tests_run'] = int(summary_match.group(1))
                    result['tests_passed'] = int(summary_match.group(2))
                    result['tests_failed'] = int(summary_match.group(3))
                    result['tests_skipped'] = int(summary_match.group(4))
                    
                # Extract failure information
                failures = []
                failed_test = None
                for line in output.split('\n'):
                    if 'Failed' in line and line.strip().startswith('X '):
                        failed_test = line.strip()
                        failures.append(failed_test)
                        
                result['failures'] = failures
            except Exception as e:
                logger.warning(f"Error parsing dotnet test results: {str(e)}")
                
        elif language == 'Go':
            # Parse Go test output
            try:
                # Count test results
                passed_count = output.count('PASS')
                failed_count = output.count('FAIL')
                
                result['tests_run'] = passed_count + failed_count
                result['tests_passed'] = passed_count
                result['tests_failed'] = failed_count
                
                # Extract failure information
                failures = []
                for line in output.split('\n'):
                    if line.startswith('--- FAIL:'):
                        failures.append(line.strip())
                        
                result['failures'] = failures
            except Exception as e:
                logger.warning(f"Error parsing Go test results: {str(e)}")
        
        # Default case: rough estimate based on output
        if result['tests_run'] == 0:
            # Simple heuristic: count lines with "pass", "fail", "error"
            pass_lines = len(re.findall(r'\bpass(?:ed)?\b', output.lower()))
            fail_lines = len(re.findall(r'\bfail(?:ed)?\b', output.lower()))
            error_lines = len(re.findall(r'\berror\b', output.lower()))
            
            result['tests_passed'] = pass_lines
            result['tests_failed'] = fail_lines + error_lines
            result['tests_run'] = pass_lines + fail_lines + error_lines
            
            if result['tests_run'] == 0:
                # If still no tests detected, use exit code
                if exit_code == 0:
                    result['tests_passed'] = 1
                else:
                    result['tests_failed'] = 1
                result['tests_run'] = 1
        
        return result
    
    def _aggregate_test_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from multiple test runs.
        
        Args:
            results: List of individual test results.
            
        Returns:
            Aggregated test results.
        """
        aggregated = {
            'status': 'passed',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'tests_skipped': 0,
            'failures': [],
            'results': results
        }
        
        for result in results:
            aggregated['tests_run'] += result.get('tests_run', 0)
            aggregated['tests_passed'] += result.get('tests_passed', 0)
            aggregated['tests_failed'] += result.get('tests_failed', 0)
            aggregated['tests_skipped'] += result.get('tests_skipped', 0)
            aggregated['failures'].extend(result.get('failures', []))
            
            if result.get('status') != 'passed':
                aggregated['status'] = 'failed'
        
        return aggregated