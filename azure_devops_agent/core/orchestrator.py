"""
Orchestrator module for Azure DevOps Integration Agent.

This is the main module that coordinates the entire task implementation workflow,
from task interpretation to pull request creation.
"""

import os
import logging
import tempfile
import shutil
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

from azure_devops_agent.core.azure_client import AzureDevOpsClient
from azure_devops_agent.core.task_processor import TaskProcessor
from azure_devops_agent.core.pr_manager import PRManager
from azure_devops_agent.repository.git_handler import GitHandler
from azure_devops_agent.implementation.implementation_manager import ImplementationManager
from azure_devops_agent.testing.test_runner import TestRunner

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Main orchestrator for the Azure DevOps Integration Agent.
    
    This class coordinates the entire workflow, including:
    - Retrieving and interpreting task details
    - Cloning and analyzing repositories
    - Implementing required changes
    - Running tests
    - Creating pull requests
    """
    
    def __init__(self, 
                 organization_url: str, 
                 personal_access_token: str,
                 project: Optional[str] = None,
                 work_dir: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            organization_url: Azure DevOps organization URL.
            personal_access_token: PAT for Azure DevOps.
            project: Default project name (optional).
            work_dir: Working directory for repositories (optional).
        """
        # Initialize the Azure DevOps client
        self.azure_client = AzureDevOpsClient(
            organization_url=organization_url,
            personal_access_token=personal_access_token,
            project=project
        )
        
        # Set up working directory
        self.work_dir = work_dir
        if not self.work_dir:
            # Create a temporary directory if none specified
            self.temp_dir = tempfile.mkdtemp(prefix='azdevops_')
            self.work_dir = self.temp_dir
        else:
            self.temp_dir = None
        
        # Initialize task processor
        self.task_processor = TaskProcessor(self.azure_client)
        
        # PR manager will be initialized when needed
        self.pr_manager = None
        
        logger.info(f"Orchestrator initialized with work directory: {self.work_dir}")
    
    def __del__(self):
        """Clean up temporary directory when the object is destroyed."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory {self.temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory: {str(e)}")
    
    def process_task(self, task_id: str) -> Dict[str, Any]:
        """
        Process an Azure DevOps task by its ID.
        
        This is the main entry point for task processing. It orchestrates the entire workflow,
        from retrieving task details to creating a pull request.
        
        Args:
            task_id: ID of the task to process.
            
        Returns:
            Dictionary with processing results.
        """
        # Start tracking time for metrics
        start_time = datetime.now()
        
        logger.info(f"Starting to process task {task_id}")
        
        try:
            # Step 1: Process task details
            task_result = self.task_processor.process_task(task_id)
            
            # Check if task needs clarification
            if task_result.get('status') == 'clarification_requested':
                return {
                    'status': 'clarification_requested',
                    'message': "Clarification requested for this task. Please check the task comments.",
                    'task_id': task_id,
                    'processing_time': str(datetime.now() - start_time)
                }
            
            # Step 2: Clone and set up repository
            repo_info = task_result.get('repository', {})
            repo_url = repo_info.get('url')
            
            if not repo_url:
                return {
                    'status': 'error',
                    'message': "Repository URL not found in task details.",
                    'task_id': task_id,
                    'processing_time': str(datetime.now() - start_time)
                }
                
            git_handler = self._setup_repository(repo_url, task_id)
            
            if not git_handler:
                return {
                    'status': 'error',
                    'message': "Failed to set up repository.",
                    'task_id': task_id,
                    'processing_time': str(datetime.now() - start_time)
                }
            
            # Step 3: Implement changes
            repo_path = git_handler.local_path
            implementation_manager = ImplementationManager(repo_path)
            
            implementation_result = implementation_manager.implement_task(task_result)
            
            # Step 4: Commit changes
            commit_hash = implementation_manager.commit_changes(task_id)
            
            # Step 5: Create pull request
            self.pr_manager = PRManager(self.azure_client, git_handler)
            
            # Get repository ID
            repository_id = self._get_repository_id(repo_info)
            
            # Create PR
            branch_name = f"task/{task_id}"
            pr_result = self.pr_manager.create_pull_request(
                task_id=task_id,
                task_details=task_result.get('task_details', {}),
                implementation_results=implementation_result,
                repository_id=repository_id,
                source_branch=branch_name,
                target_branch='main',  # This could be configurable
                project=repo_info.get('project')
            )
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            
            # Return final result
            return {
                'status': 'completed',
                'task_id': task_id,
                'implementation_result': implementation_result,
                'commit_hash': commit_hash,
                'pull_request': pr_result,
                'processing_time': str(processing_time)
            }
            
        except Exception as e:
            logger.error(f"Error processing task {task_id}: {str(e)}", exc_info=True)
            
            return {
                'status': 'error',
                'message': f"Error processing task: {str(e)}",
                'task_id': task_id,
                'processing_time': str(datetime.now() - start_time)
            }
    
    def _setup_repository(self, repo_url: str, task_id: str) -> Optional[GitHandler]:
        """
        Set up a repository for a task.
        
        Args:
            repo_url: URL of the repository.
            task_id: ID of the task.
            
        Returns:
            GitHandler instance or None if setup failed.
        """
        try:
            # Create directory for this task's repository
            repo_dir = os.path.join(self.work_dir, f"task_{task_id}")
            os.makedirs(repo_dir, exist_ok=True)
            
            # Initialize Git handler
            git_handler = GitHandler(
                repository_url=repo_url,
                local_path=repo_dir
            )
            
            # Clone repository
            git_handler.clone_repository()
            
            # Create a new branch for the task
            branch_name = f"task/{task_id}"
            git_handler.create_branch(branch_name)
            
            logger.info(f"Repository set up successfully at {repo_dir}")
            return git_handler
            
        except Exception as e:
            logger.error(f"Failed to set up repository: {str(e)}")
            return None
    
    def _get_repository_id(self, repo_info: Dict[str, Any]) -> str:
        """
        Get repository ID from repository information.
        
        Args:
            repo_info: Repository information dictionary.
            
        Returns:
            Repository ID or name.
        """
        # Try to get ID directly
        if 'id' in repo_info:
            return repo_info['id']
            
        # Try to extract from URL
        url = repo_info.get('url', '')
        
        # Pattern: https://dev.azure.com/{org}/{project}/_git/{repo}
        # or: https://{org}.visualstudio.com/{project}/_git/{repo}
        match = re.search(r'/_git/([^/]+)$', url)
        if match:
            return match.group(1)
            
        # Fall back to name if available
        if 'name' in repo_info:
            return repo_info['name']
            
        # Last resort: extract the last part of the URL
        parts = url.rstrip('/').split('/')
        return parts[-1] if parts else "unknown-repo"