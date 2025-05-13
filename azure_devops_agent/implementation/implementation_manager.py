"""
Implementation Manager module for Azure DevOps Integration Agent.

This module orchestrates the implementation process, integrating language detection,
code generation, and testing components.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Tuple
import tempfile

from azure_devops_agent.implementation.language_detector import LanguageDetector
from azure_devops_agent.implementation.code_generator import CodeGenerator
from azure_devops_agent.repository.git_handler import GitHandler

logger = logging.getLogger(__name__)

class ImplementationManager:
    """Manage the implementation of tasks in the repository."""
    
    def __init__(self, 
                 repo_path: str, 
                 code_generator: Optional[CodeGenerator] = None):
        """
        Initialize the implementation manager.
        
        Args:
            repo_path: Path to the repository.
            code_generator: CodeGenerator instance (optional).
        """
        self.repo_path = repo_path
        self.language_detector = LanguageDetector(repo_path)
        self.code_generator = code_generator or CodeGenerator()
        self.git_handler = GitHandler(repository_url="", local_path=repo_path)
        logger.info(f"Implementation manager initialized for repository at {repo_path}")
    
    def implement_task(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement a task in the repository.
        
        This method orchestrates the entire implementation process:
        1. Analyze the repository to detect languages and frameworks
        2. Determine which files to modify based on task details
        3. Generate code implementation
        4. Generate tests if required
        5. Commit changes
        
        Args:
            task_details: Details of the task to implement.
            
        Returns:
            Dictionary with implementation results.
        """
        # Analyze repository languages and frameworks
        repo_analysis = self._analyze_repository()
        
        # Enhance task details with repository analysis
        task_details.update({
            'repository_analysis': repo_analysis
        })
        
        # Determine files to modify based on task requirements
        files_to_modify = self._determine_files_to_modify(task_details)
        
        # Implement changes in each file
        implementation_results = []
        for file_info in files_to_modify:
            result = self._implement_file_changes(file_info, task_details)
            implementation_results.append(result)
            
        # Generate and run tests if required
        test_results = []
        if task_details.get('testing_required', False):
            for implementation in implementation_results:
                if implementation['status'] == 'success':
                    test_result = self._generate_and_run_tests(implementation, task_details)
                    test_results.append(test_result)
        
        # Return implementation summary
        return {
            'status': 'completed',
            'task_id': task_details.get('id'),
            'implementations': implementation_results,
            'tests': test_results,
            'repository_analysis': repo_analysis
        }
    
    def _analyze_repository(self) -> Dict[str, Any]:
        """
        Analyze the repository to detect languages and frameworks.
        
        Returns:
            Dictionary with repository analysis results.
        """
        # Detect programming languages
        languages = self.language_detector.detect_languages()
        
        # Get primary language (most used)
        primary_language = max(languages.items(), key=lambda x: x[1])[0] if languages else None
        
        # Detect frameworks for the primary language
        frameworks = {}
        if primary_language:
            frameworks = self.language_detector.detect_frameworks(primary_language)
        
        # Analyze code style for primary language
        code_style = {}
        if primary_language:
            # Get some sample files for style analysis
            file_paths = []
            for root, _, files in os.walk(self.repo_path):
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext[1:] in self.language_detector.LANGUAGE_EXTENSIONS:
                        if self.language_detector.LANGUAGE_EXTENSIONS[ext[1:]] == primary_language:
                            file_paths.append(os.path.join(root, file))
                            if len(file_paths) >= 10:  # Limit to 10 files
                                break
                if len(file_paths) >= 10:
                    break
                    
            if file_paths:
                code_style = self.language_detector.analyze_code_style(primary_language, file_paths)
        
        logger.info(f"Repository analysis: {len(languages)} languages, {len(frameworks)} frameworks detected")
        return {
            'languages': languages,
            'primary_language': primary_language,
            'frameworks': frameworks,
            'code_style': code_style
        }
    
    def _determine_files_to_modify(self, task_details: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine which files to modify based on task details.
        
        Args:
            task_details: Task details dictionary.
            
        Returns:
            List of file information dictionaries.
        """
        # Check if specific files are mentioned in the task
        files_to_modify = []
        
        # If specific files are mentioned in task requirements, use those
        if 'files_to_modify' in task_details.get('requirements', {}):
            explicit_files = task_details['requirements']['files_to_modify']
            
            for file_path in explicit_files:
                # Check if file exists
                full_path = os.path.join(self.repo_path, file_path)
                
                file_info = {
                    'path': file_path,
                    'full_path': full_path,
                    'exists': os.path.exists(full_path),
                    'action': 'modify' if os.path.exists(full_path) else 'create'
                }
                
                # Detect language if file exists or based on extension
                if file_info['exists']:
                    # Read existing content
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_info['existing_content'] = f.read()
                    
                    # Detect language
                    ext = os.path.splitext(file_path)[1][1:].lower()
                    if ext in self.language_detector.LANGUAGE_EXTENSIONS:
                        file_info['language'] = self.language_detector.LANGUAGE_EXTENSIONS[ext]
                else:
                    # Determine language based on extension for new files
                    ext = os.path.splitext(file_path)[1][1:].lower()
                    if ext in self.language_detector.LANGUAGE_EXTENSIONS:
                        file_info['language'] = self.language_detector.LANGUAGE_EXTENSIONS[ext]
                    else:
                        # Use repository's primary language as fallback
                        file_info['language'] = task_details.get('repository_analysis', {}).get('primary_language')
                
                files_to_modify.append(file_info)
                
        # If no explicit files are mentioned, try to infer based on task details
        if not files_to_modify:
            # This would be a more complex implementation in a real scenario
            # For now, we'll just indicate that we couldn't determine files
            logger.warning("No explicit files to modify, and inference not implemented")
        
        logger.info(f"Determined {len(files_to_modify)} files to modify")
        return files_to_modify
    
    def _implement_file_changes(self, 
                              file_info: Dict[str, Any], 
                              task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement changes for a single file.
        
        Args:
            file_info: Information about the file to modify.
            task_details: Task details.
            
        Returns:
            Dictionary with implementation results.
        """
        file_path = file_info['path']
        language = file_info['language']
        existing_content = file_info.get('existing_content')
        
        # Get code style for the language
        code_style = task_details.get('repository_analysis', {}).get('code_style', {})
        
        try:
            # Generate implementation
            implementation = self.code_generator.generate_implementation(
                task_details,
                language,
                code_style,
                file_path,
                existing_content
            )
            
            # Write implementation to file
            full_path = file_info['full_path']
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(implementation)
                
            logger.info(f"Successfully implemented changes for {file_path}")
            
            return {
                'status': 'success',
                'file': file_path,
                'language': language,
                'action': file_info['action'],
                'implementation': implementation
            }
            
        except Exception as e:
            logger.error(f"Error implementing changes for {file_path}: {str(e)}")
            
            return {
                'status': 'error',
                'file': file_path,
                'language': language,
                'action': file_info['action'],
                'error': str(e)
            }
    
    def _generate_and_run_tests(self, 
                              implementation_result: Dict[str, Any], 
                              task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and run tests for an implementation.
        
        Args:
            implementation_result: Result of implementation.
            task_details: Task details.
            
        Returns:
            Dictionary with test results.
        """
        if implementation_result['status'] != 'success':
            return {
                'status': 'skipped',
                'file': implementation_result['file'],
                'reason': 'Implementation failed'
            }
            
        file_path = implementation_result['file']
        language = implementation_result['language']
        implementation = implementation_result['implementation']
        
        # Determine framework (this would be more sophisticated in a real implementation)
        framework = None
        if language in ['JavaScript', 'TypeScript']:
            if any(f in task_details.get('repository_analysis', {}).get('frameworks', {}) for f in ['Jest', 'Mocha']):
                framework = 'Jest' if 'Jest' in task_details['repository_analysis']['frameworks'] else 'Mocha'
        elif language == 'Python':
            framework = 'pytest' if 'pytest' in task_details.get('repository_analysis', {}).get('frameworks', {}) else 'unittest'
        
        try:
            # Generate tests
            tests = self.code_generator.generate_unit_tests(
                implementation,
                language,
                file_path,
                framework
            )
            
            # Determine test file path
            test_file_path = self._get_test_file_path(file_path, language)
            full_test_path = os.path.join(self.repo_path, test_file_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_test_path), exist_ok=True)
            
            # Write tests to file
            with open(full_test_path, 'w', encoding='utf-8') as f:
                f.write(tests)
                
            # Run tests - in a real implementation, this would use the testing module
            # to actually execute the tests
            test_result = {
                'status': 'generated',  # We're not actually running tests in this simplified example
                'file': test_file_path,
                'tests': tests
            }
            
            logger.info(f"Generated tests for {file_path} at {test_file_path}")
            return test_result
            
        except Exception as e:
            logger.error(f"Error generating/running tests for {file_path}: {str(e)}")
            
            return {
                'status': 'error',
                'file': file_path,
                'error': str(e)
            }
    
    def _get_test_file_path(self, implementation_path: str, language: str) -> str:
        """
        Determine test file path based on implementation path and language.
        
        Args:
            implementation_path: Path to the implementation file.
            language: Programming language.
            
        Returns:
            Path for the test file.
        """
        # This duplicates logic from CodeGenerator._get_test_file_path
        # In a real implementation, this would be refactored to avoid duplication
        base_name = os.path.basename(implementation_path)
        dir_name = os.path.dirname(implementation_path)
        
        # Handle language-specific test file naming conventions
        if language in ['JavaScript', 'TypeScript']:
            name, ext = os.path.splitext(base_name)
            return os.path.join(dir_name, f"{name}.test{ext}")
        elif language == 'Python':
            name, ext = os.path.splitext(base_name)
            return os.path.join(dir_name, f"test_{name}{ext}")
        elif language in ['Java', 'Kotlin']:
            name, ext = os.path.splitext(base_name)
            return os.path.join(dir_name, f"{name}Test{ext}")
        elif language == 'C#':
            name, ext = os.path.splitext(base_name)
            return os.path.join(dir_name, f"{name}Tests{ext}")
        
        # Default case
        name, ext = os.path.splitext(base_name)
        return os.path.join(dir_name, f"{name}Test{ext}")
    
    def commit_changes(self, task_id: str, message: Optional[str] = None) -> str:
        """
        Commit implemented changes to Git.
        
        Args:
            task_id: ID of the task.
            message: Commit message (optional).
            
        Returns:
            Commit hash.
        """
        # Stage all changes
        # In a real implementation, this would be more selective
        self.git_handler.add_files(['.'])
        
        # Create commit message if not provided
        if not message:
            message = f"Implement task #{task_id}\n\nImplemented by Azure DevOps AI Agent"
            
        # Commit changes
        commit_hash = self.git_handler.commit_changes(message)
        
        logger.info(f"Committed changes for task {task_id}: {commit_hash}")
        return commit_hash