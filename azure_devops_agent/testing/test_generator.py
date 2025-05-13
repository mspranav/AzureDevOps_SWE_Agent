"""
Test Generator module for Azure DevOps Integration Agent.

This module generates unit tests for implementations across different programming languages.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any, Tuple

# In a real implementation, this would use a client for OpenAI, Azure OpenAI API, or similar
from azure_devops_agent.implementation.code_generator import AIModelClient

logger = logging.getLogger(__name__)

class TestGenerator:
    """Generate unit tests for implementations across multiple programming languages."""
    
    # Test framework templates by language
    TEST_TEMPLATES = {
        'JavaScript': {
            'Jest': {
                'import': "const {name} = require('{path}');\n\n",
                'describe': "describe('{name}', () => {\n{tests}\n});\n",
                'test': "  test('{description}', () => {\n{content}\n  });\n",
                'assertion': "    expect({actual}).{matcher}({expected});\n"
            }
        },
        'TypeScript': {
            'Jest': {
                'import': "import {name} from '{path}';\n\n",
                'describe': "describe('{name}', () => {\n{tests}\n});\n",
                'test': "  test('{description}', () => {\n{content}\n  });\n",
                'assertion': "    expect({actual}).{matcher}({expected});\n"
            }
        },
        'Python': {
            'pytest': {
                'import': "import pytest\nfrom {module_path} import {name}\n\n",
                'test': "def test_{test_name}():\n{content}\n",
                'assertion': "    assert {actual} {operator} {expected}\n"
            },
            'unittest': {
                'import': "import unittest\nfrom {module_path} import {name}\n\n",
                'class': "class Test{name}(unittest.TestCase):\n{tests}\n",
                'test': "    def test_{test_name}(self):\n{content}\n",
                'assertion': "        self.{assertion_type}({actual}, {expected})\n"
            }
        },
        'Java': {
            'JUnit': {
                'import': "import org.junit.Test;\nimport org.junit.Assert;\nimport static org.junit.Assert.*;\n",
                'class': "public class {name}Test {\n{tests}\n}\n",
                'test': "    @Test\n    public void test{test_name}() {\n{content}\n    }\n",
                'assertion': "        Assert.{assertion_type}({expected}, {actual});\n"
            }
        },
        'C#': {
            'NUnit': {
                'import': "using NUnit.Framework;\nusing System;\n",
                'class': "[TestFixture]\npublic class {name}Tests\n{\n{tests}\n}\n",
                'test': "    [Test]\n    public void Test{test_name}()\n    {\n{content}\n    }\n",
                'assertion': "        Assert.{assertion_type}({expected}, {actual});\n"
            },
            'xUnit': {
                'import': "using Xunit;\nusing System;\n",
                'class': "public class {name}Tests\n{\n{tests}\n}\n",
                'test': "    [Fact]\n    public void Test{test_name}()\n    {\n{content}\n    }\n",
                'assertion': "        Assert.{assertion_type}({expected}, {actual});\n"
            }
        }
    }
    
    def __init__(self, ai_model_client: Optional[AIModelClient] = None):
        """
        Initialize the test generator.
        
        Args:
            ai_model_client: Client for AI model API (optional).
        """
        self.ai_model_client = ai_model_client or AIModelClient()
        logger.info("Test generator initialized")
    
    def generate_tests(self,
                     implementation: str,
                     language: str,
                     framework: str,
                     file_path: str,
                     class_or_function_name: str,
                     test_file_path: str) -> str:
        """
        Generate unit tests for an implementation.
        
        Args:
            implementation: Code implementation to test.
            language: Programming language.
            framework: Testing framework.
            file_path: Path to the implementation file.
            class_or_function_name: Name of the class or function to test.
            test_file_path: Path where the test file will be written.
            
        Returns:
            Generated test code.
        """
        # Create prompt for the AI model
        prompt = self._create_test_prompt(
            implementation,
            language,
            framework,
            file_path,
            class_or_function_name,
            test_file_path
        )
        
        # Generate tests using the AI model
        generated_tests = self.ai_model_client.generate_code(prompt)
        
        # In a real implementation, we would post-process the generated code
        # to ensure it follows the framework conventions and includes all necessary imports
        
        logger.info(f"Generated tests for {class_or_function_name} using {framework}")
        return generated_tests
    
    def _create_test_prompt(self,
                          implementation: str,
                          language: str,
                          framework: str,
                          file_path: str,
                          class_or_function_name: str,
                          test_file_path: str) -> str:
        """
        Create a prompt for the AI model to generate tests.
        
        Args:
            implementation: Code implementation to test.
            language: Programming language.
            framework: Testing framework.
            file_path: Path to the implementation file.
            class_or_function_name: Name of the class or function to test.
            test_file_path: Path where the test file will be written.
            
        Returns:
            Test generation prompt.
        """
        prompt = f"""
Generate unit tests for the following {language} code using the {framework} testing framework:

```{language.lower()}
{implementation}
```

Implementation file path: {file_path}
Test file path: {test_file_path}
Class or function name to test: {class_or_function_name}

Please include:
- Appropriate imports and setup
- Test cases covering the main functionality
- Edge cases
- Exception testing where appropriate
- Mocks or stubs for external dependencies

Follow these guidelines:
- Use {framework} assertions and conventions
- Make tests deterministic and independent
- Include clear test names describing what is being tested
- Add comments explaining test scenarios
- Use standard naming conventions for test files and functions in {language}
"""
        
        # Add language and framework specific instructions
        if language in ['JavaScript', 'TypeScript']:
            prompt += """
JavaScript/TypeScript Testing Guidelines:
- Use describe() to group related tests
- Use test() or it() for individual test cases
- Use expect().toBe(), expect().toEqual(), etc. for assertions
- Mock external dependencies with jest.mock() or similar
"""
        elif language == 'Python':
            if framework == 'pytest':
                prompt += """
Python pytest Guidelines:
- Use descriptive function names with test_ prefix
- Use assert statements directly
- Use fixtures for setup and teardown
- Use monkeypatch for mocking
"""
            elif framework == 'unittest':
                prompt += """
Python unittest Guidelines:
- Create a class inheriting from unittest.TestCase
- Use setUp and tearDown methods for setup and teardown
- Use self.assertEqual(), self.assertTrue(), etc. for assertions
- Use unittest.mock for mocking
"""
        elif language in ['Java', 'Kotlin']:
            prompt += """
Java/Kotlin JUnit Guidelines:
- Use @Test annotation for test methods
- Use @Before/@BeforeEach for setup
- Use @After/@AfterEach for teardown
- Use Assert methods for assertions
- Use Mockito for mocking if needed
"""
        elif language == 'C#':
            prompt += """
C# Testing Guidelines:
- Use appropriate test attributes ([Test], [Fact], etc.)
- Use Assert.AreEqual(), Assert.IsTrue(), etc. for assertions
- Use setup and teardown methods as appropriate
- Use mocking frameworks like Moq if needed
"""
            
        return prompt
    
    def generate_test_from_template(self,
                                  language: str,
                                  framework: str,
                                  class_or_function_name: str,
                                  file_path: str,
                                  test_cases: List[Dict[str, Any]]) -> str:
        """
        Generate tests using built-in templates rather than AI model.
        
        Args:
            language: Programming language.
            framework: Testing framework.
            class_or_function_name: Name of the class or function to test.
            file_path: Path to the implementation file.
            test_cases: List of test case definitions.
            
        Returns:
            Generated test code.
        """
        if language not in self.TEST_TEMPLATES or framework not in self.TEST_TEMPLATES[language]:
            logger.warning(f"No template available for {language}/{framework}, using AI generation instead")
            # This would call the AI model in a real implementation
            return f"# Generated tests for {class_or_function_name} using {framework}"
            
        templates = self.TEST_TEMPLATES[language][framework]
        
        # Generate imports
        result = ""
        if 'import' in templates:
            if language in ['JavaScript', 'TypeScript']:
                rel_path = os.path.relpath(file_path, os.path.dirname(file_path))
                if not rel_path.startswith('.'):
                    rel_path = './' + rel_path
                result += templates['import'].format(name=class_or_function_name, path=rel_path)
            elif language == 'Python':
                module_path = os.path.splitext(os.path.basename(file_path))[0]
                result += templates['import'].format(module_path=module_path, name=class_or_function_name)
            else:
                result += templates['import']
        
        # Generate test class if needed
        if 'class' in templates:
            test_code = ""
            for test_case in test_cases:
                test_name = test_case['name']
                content = ""
                for step in test_case['steps']:
                    if step['type'] == 'assertion':
                        content += templates['assertion'].format(
                            assertion_type=step['assertion_type'],
                            expected=step['expected'],
                            actual=step['actual'],
                            operator=step.get('operator', '==')
                        )
                    else:
                        content += ' ' * 8 + step['code'] + '\n'
                
                test_code += templates['test'].format(
                    test_name=test_name,
                    content=content
                )
            
            result += templates['class'].format(
                name=class_or_function_name,
                tests=test_code
            )
        # Generate standalone test functions
        elif 'test' in templates:
            for test_case in test_cases:
                test_name = test_case['name']
                content = ""
                for step in test_case['steps']:
                    if step['type'] == 'assertion':
                        content += templates['assertion'].format(
                            assertion_type=step['assertion_type'],
                            expected=step['expected'],
                            actual=step['actual'],
                            operator=step.get('operator', '==')
                        )
                    else:
                        content += ' ' * 4 + step['code'] + '\n'
                
                result += templates['test'].format(
                    test_name=test_name,
                    content=content
                )
        
        # For JavaScript/TypeScript with describe blocks
        elif 'describe' in templates:
            tests_code = ""
            for test_case in test_cases:
                test_content = ""
                for step in test_case['steps']:
                    if step['type'] == 'assertion':
                        test_content += templates['assertion'].format(
                            matcher=step['matcher'],
                            expected=step['expected'],
                            actual=step['actual']
                        )
                    else:
                        test_content += ' ' * 4 + step['code'] + '\n'
                
                tests_code += templates['test'].format(
                    description=test_case['description'],
                    content=test_content
                )
            
            result += templates['describe'].format(
                name=class_or_function_name,
                tests=tests_code
            )
        
        return result