"""
Code Generator module for Azure DevOps Integration Agent.

This module is responsible for generating code implementations
for tasks across multiple programming languages, using AI models
and language-specific patterns.
"""

import os
import logging
import re
import json
from typing import Dict, List, Optional, Any, Union, Tuple
import tempfile

# In a real implementation, this would use a client for OpenAI, Azure OpenAI API, or similar
# Here, we'll provide a simplified interface for illustration
class AIModelClient:
    def generate_code(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Generate code using an AI model.
        
        Args:
            prompt: The prompt for code generation.
            max_tokens: Maximum tokens for generation.
            
        Returns:
            Generated code as a string.
        """
        # Placeholder - in a real implementation, this would make API calls
        # to an AI model like OpenAI or Azure OpenAI
        return f"# Generated code placeholder for prompt: {prompt[:20]}..."

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Generate code implementations across multiple programming languages."""
    
    def __init__(self, ai_model_client: Optional[AIModelClient] = None):
        """
        Initialize the code generator.
        
        Args:
            ai_model_client: Client for AI model API (optional).
        """
        self.ai_model_client = ai_model_client or AIModelClient()
        logger.info("Code generator initialized")
        
    def generate_implementation(self, 
                              task_details: Dict[str, Any], 
                              language: str,
                              code_style: Dict[str, Any],
                              file_path: str,
                              existing_code: Optional[str] = None) -> str:
        """
        Generate code implementation for a given task and language.
        
        Args:
            task_details: Details of the task to implement.
            language: The programming language to use.
            code_style: Code style information for the language.
            file_path: Path to the file to modify/create.
            existing_code: Existing code to modify (None for new files).
            
        Returns:
            Generated code implementation.
        """
        # Determine which language-specific generator to use
        if language in ['JavaScript', 'TypeScript', 'JavaScript (React)', 'TypeScript (React)']:
            return self._generate_js_ts_implementation(task_details, language, code_style, file_path, existing_code)
        elif language == 'Python':
            return self._generate_python_implementation(task_details, code_style, file_path, existing_code)
        elif language in ['Java', 'Kotlin']:
            return self._generate_java_implementation(task_details, language, code_style, file_path, existing_code)
        elif language == 'C#':
            return self._generate_csharp_implementation(task_details, code_style, file_path, existing_code)
        elif language == 'Go':
            return self._generate_go_implementation(task_details, code_style, file_path, existing_code)
        elif language == 'Ruby':
            return self._generate_ruby_implementation(task_details, code_style, file_path, existing_code)
        else:
            return self._generate_generic_implementation(task_details, language, code_style, file_path, existing_code)
    
    def _create_prompt_for_language(self, 
                                   task_details: Dict[str, Any], 
                                   language: str,
                                   code_style: Dict[str, Any],
                                   file_path: str,
                                   existing_code: Optional[str]) -> str:
        """
        Create a language-specific prompt for the AI model.
        
        Args:
            task_details: Task details dictionary.
            language: Programming language.
            code_style: Code style information.
            file_path: File path.
            existing_code: Existing code (None for new files).
            
        Returns:
            Formatted prompt string.
        """
        # Common prompt elements
        prompt = f"""
Task: {task_details.get('title', 'Implement a feature')}

Description:
{task_details.get('description', 'No description provided')}

Acceptance Criteria:
{task_details.get('acceptance_criteria', 'No acceptance criteria provided')}

Programming Language: {language}

File Path: {file_path}

Code Style Guide:
"""
        
        # Add language-specific style guide
        for key, value in code_style.items():
            if isinstance(value, dict):
                prompt += f"- {key}:\n"
                for subkey, subval in value.items():
                    prompt += f"  - {subkey}: {subval}\n"
            else:
                prompt += f"- {key}: {value}\n"
        
        # Add existing code if modifying a file
        if existing_code:
            prompt += f"\nExisting Code:\n```{language.lower()}\n{existing_code}\n```\n"
            prompt += "\nPlease modify the existing code to implement the required functionality."
        else:
            prompt += "\nPlease create a new file with the implementation for the required functionality."
        
        # Add language-specific frameworks if detected
        frameworks = task_details.get('frameworks', [])
        if frameworks:
            prompt += "\n\nDetected Frameworks:\n"
            for framework in frameworks:
                prompt += f"- {framework}\n"
        
        # Add instructions for testing
        if task_details.get('testing_required', False):
            prompt += "\nRequirements for Testing:\n- Include unit tests for the implementation\n"
        
        # Add additional context about the task
        if 'additional_context' in task_details:
            prompt += f"\nAdditional Context:\n{task_details['additional_context']}\n"
        
        return prompt
    
    def _generate_js_ts_implementation(self, 
                                     task_details: Dict[str, Any], 
                                     language: str,
                                     code_style: Dict[str, Any],
                                     file_path: str,
                                     existing_code: Optional[str]) -> str:
        """
        Generate JavaScript/TypeScript implementation.
        
        Args:
            task_details: Task details.
            language: JS or TS variant.
            code_style: Code style information.
            file_path: File path.
            existing_code: Existing code (None for new files).
            
        Returns:
            Generated implementation.
        """
        is_typescript = 'TypeScript' in language
        is_react = 'React' in language
        
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, language, code_style, file_path, existing_code)
        
        # Add TypeScript-specific instructions
        if is_typescript:
            prompt += "\nPlease use proper TypeScript types and interfaces. Ensure type safety throughout the implementation."
        
        # Add React-specific instructions
        if is_react:
            prompt += "\nImplement using React best practices. Consider using hooks where appropriate."
            
            # Check if this is a functional or class component based on existing code
            if existing_code and "extends React.Component" in existing_code:
                prompt += "\nThis is a class component. Please maintain this pattern in your implementation."
            elif existing_code:
                prompt += "\nThis is a functional component. Please maintain this pattern and use hooks appropriately."
        
        # Add semicolon preference
        if 'semicolons' in code_style:
            prompt += f"\nPlease {'use' if code_style['semicolons'] else 'omit'} semicolons at the end of statements."
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        # In a real implementation, we would post-process the generated code
        # to ensure it follows the code style exactly
        
        return generated_code
    
    def _generate_python_implementation(self, 
                                      task_details: Dict[str, Any],
                                      code_style: Dict[str, Any],
                                      file_path: str,
                                      existing_code: Optional[str]) -> str:
        """
        Generate Python implementation.
        
        Args:
            task_details: Task details.
            code_style: Code style information.
            file_path: File path.
            existing_code: Existing code (None for new files).
            
        Returns:
            Generated implementation.
        """
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, "Python", code_style, file_path, existing_code)
        
        # Add Python-specific instructions
        prompt += "\nPlease follow PEP 8 guidelines except where they conflict with the provided code style."
        
        # Add string quote preference
        if 'string_quotes' in code_style:
            prompt += f"\nPlease use {code_style['string_quotes']} quotes for strings."
            
        # Add docstring preference
        prompt += "\nInclude docstrings for all functions, classes, and modules using triple double-quotes."
        
        # Add type hints preference if Python 3
        prompt += "\nPlease use type hints for function parameters and return values."
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def _generate_java_implementation(self, 
                                    task_details: Dict[str, Any],
                                    language: str,
                                    code_style: Dict[str, Any],
                                    file_path: str,
                                    existing_code: Optional[str]) -> str:
        """
        Generate Java/Kotlin implementation.
        
        Args:
            task_details: Task details.
            language: Java or Kotlin.
            code_style: Code style information.
            file_path: File path.
            existing_code: Existing code (None for new files).
            
        Returns:
            Generated implementation.
        """
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, language, code_style, file_path, existing_code)
        
        # Add Java-specific instructions
        if language == 'Java':
            prompt += "\nPlease follow standard Java conventions. Include proper exception handling and JavaDoc comments."
            
            # Extract package name from file path or existing code
            package_name = ""
            if existing_code and "package " in existing_code:
                package_match = re.search(r'package\s+([a-z0-9_.]+);', existing_code)
                if package_match:
                    package_name = package_match.group(1)
            elif file_path:
                # Extract package name from file path (src/main/java/com/example/...)
                parts = file_path.split(os.path.sep)
                if 'java' in parts:
                    java_index = parts.index('java')
                    if java_index < len(parts) - 1:
                        package_name = '.'.join(parts[java_index+1:-1])
            
            if package_name:
                prompt += f"\nUse package: {package_name}"
        
        # Add Kotlin-specific instructions
        elif language == 'Kotlin':
            prompt += "\nPlease use idiomatic Kotlin. Use val for immutable variables and data classes where appropriate."
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def _generate_csharp_implementation(self, 
                                      task_details: Dict[str, Any],
                                      code_style: Dict[str, Any],
                                      file_path: str,
                                      existing_code: Optional[str]) -> str:
        """Generate C# implementation."""
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, "C#", code_style, file_path, existing_code)
        
        # Add C#-specific instructions
        prompt += "\nPlease follow C# coding conventions. Use proper properties, LINQ where appropriate, and include XML documentation comments."
        
        # Extract namespace from existing code
        namespace = ""
        if existing_code and "namespace " in existing_code:
            namespace_match = re.search(r'namespace\s+([a-zA-Z0-9_.]+)', existing_code)
            if namespace_match:
                namespace = namespace_match.group(1)
                prompt += f"\nUse namespace: {namespace}"
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def _generate_go_implementation(self, 
                                  task_details: Dict[str, Any],
                                  code_style: Dict[str, Any],
                                  file_path: str,
                                  existing_code: Optional[str]) -> str:
        """Generate Go implementation."""
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, "Go", code_style, file_path, existing_code)
        
        # Add Go-specific instructions
        prompt += "\nPlease follow Go style guidelines. Use error handling patterns consistent with the codebase."
        
        # Extract package name from existing code
        package_name = ""
        if existing_code and "package " in existing_code:
            package_match = re.search(r'package\s+([a-zA-Z0-9_]+)', existing_code)
            if package_match:
                package_name = package_match.group(1)
                prompt += f"\nUse package: {package_name}"
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def _generate_ruby_implementation(self, 
                                    task_details: Dict[str, Any],
                                    code_style: Dict[str, Any],
                                    file_path: str,
                                    existing_code: Optional[str]) -> str:
        """Generate Ruby implementation."""
        # Create specialized prompt
        prompt = self._create_prompt_for_language(task_details, "Ruby", code_style, file_path, existing_code)
        
        # Add Ruby-specific instructions
        prompt += "\nPlease follow Ruby style guidelines. Use snake_case for methods and variables."
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def _generate_generic_implementation(self, 
                                      task_details: Dict[str, Any],
                                      language: str,
                                      code_style: Dict[str, Any],
                                      file_path: str,
                                      existing_code: Optional[str]) -> str:
        """
        Generate implementation for languages without specific handlers.
        
        Args:
            task_details: Task details.
            language: Programming language.
            code_style: Code style information.
            file_path: File path.
            existing_code: Existing code (None for new files).
            
        Returns:
            Generated implementation.
        """
        # Create a generic prompt
        prompt = self._create_prompt_for_language(task_details, language, code_style, file_path, existing_code)
        
        # Add generic instructions
        prompt += f"\nPlease implement this in {language} following best practices for that language."
        
        # Generate code using the AI model
        generated_code = self.ai_model_client.generate_code(prompt)
        
        return generated_code
    
    def generate_unit_tests(self, 
                          implementation: str, 
                          language: str,
                          file_path: str,
                          testing_framework: Optional[str] = None) -> str:
        """
        Generate unit tests for an implementation.
        
        Args:
            implementation: The code implementation to test.
            language: The programming language of the implementation.
            file_path: Path to the implementation file.
            testing_framework: Preferred testing framework (optional).
            
        Returns:
            Generated unit tests.
        """
        # Determine test file path
        test_file_path = self._get_test_file_path(file_path, language)
        
        # Determine appropriate testing framework if not specified
        if not testing_framework:
            testing_framework = self._determine_testing_framework(language)
        
        # Create prompt for test generation
        prompt = f"""
Generate unit tests for the following {language} implementation:

```{language.lower()}
{implementation}
```

Test file path: {test_file_path}
Testing framework: {testing_framework}

Please include:
- Comprehensive test cases covering the main functionality
- Edge cases and error handling
- Mock objects where appropriate
- Setup and teardown as needed
"""
        
        # Generate tests using the AI model
        generated_tests = self.ai_model_client.generate_code(prompt)
        
        return generated_tests
    
    def _get_test_file_path(self, implementation_path: str, language: str) -> str:
        """
        Determine the appropriate test file path based on the implementation path.
        
        Args:
            implementation_path: Path to the implementation file.
            language: Programming language.
            
        Returns:
            Path for the test file.
        """
        base_name = os.path.basename(implementation_path)
        dir_name = os.path.dirname(implementation_path)
        
        # Handle language-specific test file naming conventions
        if language in ['JavaScript', 'TypeScript']:
            # For JS/TS, typically tests are in a __tests__ directory or have .test.js extension
            name, ext = os.path.splitext(base_name)
            
            # Check for common test directory patterns
            if 'src' in dir_name.split(os.path.sep):
                # src/component.js -> src/__tests__/component.test.js
                src_index = dir_name.split(os.path.sep).index('src')
                parts = dir_name.split(os.path.sep)
                test_dir = os.path.sep.join(parts[:src_index+1] + ['__tests__'] + parts[src_index+1:])
                return os.path.join(test_dir, f"{name}.test{ext}")
            else:
                # Default to adding .test before the extension
                return os.path.join(dir_name, f"{name}.test{ext}")
                
        elif language == 'Python':
            # For Python, tests are typically in a tests directory with test_ prefix
            name, ext = os.path.splitext(base_name)
            
            # Check for common test directory patterns
            if any(d in dir_name.split(os.path.sep) for d in ['src', 'lib']):
                # src/module.py -> tests/test_module.py
                for common_dir in ['src', 'lib']:
                    if common_dir in dir_name.split(os.path.sep):
                        common_index = dir_name.split(os.path.sep).index(common_dir)
                        parts = dir_name.split(os.path.sep)
                        test_dir = os.path.sep.join(parts[:common_index] + ['tests'])
                        return os.path.join(test_dir, f"test_{name}{ext}")
            
            # Default to test_ prefix in the same directory
            return os.path.join(dir_name, f"test_{name}{ext}")
                
        elif language in ['Java', 'Kotlin']:
            # For Java, tests are typically in src/test/java mirroring src/main/java
            name, ext = os.path.splitext(base_name)
            if 'src/main/java' in dir_name:
                test_dir = dir_name.replace('src/main/java', 'src/test/java')
                return os.path.join(test_dir, f"{name}Test{ext}")
            else:
                return os.path.join(dir_name, f"{name}Test{ext}")
                
        elif language == 'C#':
            # For C#, tests are often in a separate project with .Tests suffix
            name, ext = os.path.splitext(base_name)
            parts = dir_name.split(os.path.sep)
            
            # Try to find the project directory
            for i, part in enumerate(parts):
                if part.endswith('.csproj') or part.endswith('.sln'):
                    test_project = f"{part}.Tests"
                    test_dir = os.path.sep.join(parts[:i] + [test_project] + parts[i+1:])
                    return os.path.join(test_dir, f"{name}Tests{ext}")
            
            # Default to adding Tests suffix
            return os.path.join(dir_name, f"{name}Tests{ext}")
        
        # Default case: add "Test" suffix to the file name
        name, ext = os.path.splitext(base_name)
        return os.path.join(dir_name, f"{name}Test{ext}")
    
    def _determine_testing_framework(self, language: str) -> str:
        """
        Determine the appropriate testing framework for a language.
        
        Args:
            language: Programming language.
            
        Returns:
            Name of an appropriate testing framework.
        """
        # Default testing frameworks by language
        frameworks = {
            'JavaScript': 'Jest',
            'TypeScript': 'Jest',
            'Python': 'pytest',
            'Java': 'JUnit',
            'Kotlin': 'JUnit',
            'C#': 'NUnit',
            'Go': 'Go testing package',
            'Ruby': 'RSpec',
            'PHP': 'PHPUnit',
            'Rust': 'Rust Test',
            'Swift': 'XCTest'
        }
        
        return frameworks.get(language, 'standard testing library')
    
    def generate_documentation(self, 
                             implementation: str, 
                             language: str,
                             task_details: Dict[str, Any]) -> str:
        """
        Generate documentation for an implementation.
        
        Args:
            implementation: The code implementation.
            language: The programming language.
            task_details: Task details.
            
        Returns:
            Generated documentation.
        """
        # Create prompt for documentation generation
        prompt = f"""
Generate documentation for the following {language} implementation:

```{language.lower()}
{implementation}
```

Task: {task_details.get('title', '')}

Description:
{task_details.get('description', '')}

Please provide documentation that includes:
- Overview of the implementation
- Usage examples
- Explanation of key functions/classes
- Notes on design decisions
"""
        
        # Generate documentation using the AI model
        generated_docs = self.ai_model_client.generate_code(prompt)
        
        return generated_docs