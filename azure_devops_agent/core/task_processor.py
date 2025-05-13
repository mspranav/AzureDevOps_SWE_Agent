"""
Task Processor module for Azure DevOps Integration Agent.

This module handles the processing of Azure DevOps tasks, including
interpreting task details and orchestrating the implementation workflow.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Tuple

from azure_devops_agent.core.azure_client import AzureDevOpsClient
from azure_devops_agent.repository.git_handler import GitHandler

logger = logging.getLogger(__name__)

class TaskProcessor:
    """Process and orchestrate Azure DevOps tasks."""
    
    def __init__(self, azure_client: AzureDevOpsClient):
        """
        Initialize the task processor.
        
        Args:
            azure_client: An initialized AzureDevOpsClient instance.
        """
        self.azure_client = azure_client
        
    def process_task(self, work_item_id: int) -> Dict[str, Any]:
        """
        Process an Azure DevOps task by its ID.
        
        This is the main entry point for task processing. It retrieves task details,
        analyzes requirements, and orchestrates the implementation workflow.
        
        Args:
            work_item_id: The ID of the task to process.
            
        Returns:
            Dictionary with processing result details.
        """
        logger.info(f"Starting to process task {work_item_id}")
        
        # Get task details
        work_item = self.azure_client.get_work_item(work_item_id)
        task_details = self.azure_client.extract_task_details(work_item)
        
        # Analyze task requirements
        requirements = self._analyze_requirements(task_details)
        
        # Check if task needs clarification
        missing_info = self._check_for_missing_information(task_details, requirements)
        if missing_info:
            self._request_clarification(work_item_id, missing_info)
            return {
                'status': 'clarification_requested',
                'missing_information': missing_info,
                'task_id': work_item_id
            }
        
        # Determine repository to work on
        repository_info = self._determine_repository(task_details)
        
        # Results to be returned
        result = {
            'status': 'initialized',
            'task_id': work_item_id,
            'task_details': task_details,
            'requirements': requirements,
            'repository': repository_info
        }
        
        logger.info(f"Task {work_item_id} processed successfully")
        return result
    
    def _analyze_requirements(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the task details to extract requirements.
        
        This method parses the task description and acceptance criteria to identify:
        - What files need to be modified
        - What functionality needs to be implemented
        - Testing requirements
        - Documentation requirements
        
        Args:
            task_details: Task details dictionary.
            
        Returns:
            Dictionary containing parsed requirements.
        """
        description = task_details.get('description', '')
        acceptance_criteria = task_details.get('acceptance_criteria', '')
        
        # Combine description and acceptance criteria for analysis
        text_to_analyze = f"{description}\n{acceptance_criteria}"
        
        # Extract potential file paths mentioned in the task
        file_patterns = [
            r'(?:in|modify|update|create|the file|file)[:\s]+`?([a-zA-Z0-9_\-./\\]+\.[a-zA-Z0-9]+)`?',
            r'([a-zA-Z0-9_\-./\\]+\.[a-zA-Z]{1,5})\b(?:\s+file)?'
        ]
        
        files_to_modify = []
        for pattern in file_patterns:
            matches = re.findall(pattern, text_to_analyze)
            files_to_modify.extend(matches)
        
        # Extract testing requirements
        testing_required = 'test' in text_to_analyze.lower()
        
        # Basic requirements extraction
        requirements = {
            'files_to_modify': list(set(files_to_modify)),  # Remove duplicates
            'testing_required': testing_required,
            'description_summary': description[:500] + '...' if len(description) > 500 else description,
        }
        
        logger.info(f"Analyzed requirements: {len(requirements['files_to_modify'])} files identified")
        return requirements
    
    def _check_for_missing_information(self, 
                                     task_details: Dict[str, Any], 
                                     requirements: Dict[str, Any]) -> List[str]:
        """
        Check if there is missing information that requires clarification.
        
        Args:
            task_details: Task details dictionary.
            requirements: Parsed requirements dictionary.
            
        Returns:
            List of missing information items, empty if all required info is present.
        """
        missing_info = []
        
        # Check for repository information
        if 'repository' not in task_details:
            missing_info.append("Repository information is missing. Please specify which repository should be modified.")
        
        # Check if task description is too vague
        description = task_details.get('description', '')
        if len(description) < 50:  # Very basic heuristic
            missing_info.append("Task description is too brief. Please provide more details about what needs to be implemented.")
            
        # Check for acceptance criteria
        if not task_details.get('acceptance_criteria'):
            missing_info.append("Acceptance criteria are missing. Please specify how to verify that the task is completed correctly.")
        
        logger.info(f"Missing information check: {len(missing_info)} items missing")
        return missing_info
    
    def _request_clarification(self, work_item_id: int, missing_info: List[str]) -> None:
        """
        Add a comment to the work item requesting clarification.
        
        Args:
            work_item_id: The ID of the work item.
            missing_info: List of missing information items.
        """
        comment = "I need some clarification before I can implement this task:\n\n"
        for item in missing_info:
            comment += f"- {item}\n"
        comment += "\nPlease provide this information so I can complete the task."
        
        self.azure_client.add_comment_to_work_item(work_item_id, comment)
        logger.info(f"Requested clarification for task {work_item_id}")
    
    def _determine_repository(self, task_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine which repository to work with for the task.
        
        Args:
            task_details: Task details dictionary.
            
        Returns:
            Dictionary with repository information.
        """
        repo_info = task_details.get('repository', {})
        
        # If no repository information is available, this will return minimal info
        # The actual implementation should handle this case better
        return {
            'url': repo_info.get('url', ''),
            'name': repo_info.get('name', ''),
            'project': task_details.get('project', self.azure_client.project)
        }
    
    def execute_implementation_workflow(self, 
                                      task_id: int,
                                      repository_info: Dict[str, Any],
                                      requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the implementation workflow for a task.
        
        This method orchestrates the entire implementation process:
        1. Clone/access the repository
        2. Create a new branch
        3. Implement the required changes
        4. Run tests
        5. Create a pull request
        
        Args:
            task_id: The ID of the task.
            repository_info: Repository information dictionary.
            requirements: Task requirements dictionary.
            
        Returns:
            Dictionary with workflow execution results.
        """
        # This is just a skeleton and will be expanded
        logger.info(f"Starting implementation workflow for task {task_id}")
        
        # Initialize Git handler
        git_handler = GitHandler(repository_info['url'])
        
        # Clone repository and create branch
        local_repo_path = git_handler.clone_repository()
        branch_name = f"task/{task_id}"
        git_handler.create_branch(branch_name)
        
        # TODO: Implement changes in the repository
        # This will use the implementation module
        
        # TODO: Run tests
        # This will use the testing module
        
        # TODO: Create pull request
        # This will use the azure_client
        
        return {
            'status': 'implemented',
            'task_id': task_id,
            'pull_request': {
                'created': False,  # placeholder
                'url': '',  # placeholder
            }
        }