"""
Azure DevOps API Client for the Integration Agent.

This module provides functionality to interact with Azure DevOps services,
read task details, and create pull requests.
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from azure.devops.connection import Connection
from azure.devops.v6_0.work_item_tracking.models import WorkItem, WorkItemExpand
from azure.devops.v6_0.git.models import GitPullRequest, GitRepository
from msrest.authentication import BasicAuthentication

logger = logging.getLogger(__name__)

class AzureDevOpsClient:
    """Client for interacting with Azure DevOps API."""

    def __init__(self, 
                 organization_url: str, 
                 personal_access_token: str,
                 project: Optional[str] = None):
        """
        Initialize the Azure DevOps client.
        
        Args:
            organization_url: The URL of the Azure DevOps organization.
            personal_access_token: PAT with appropriate permissions.
            project: The default project to work with (optional).
        """
        self.organization_url = organization_url
        self.credentials = BasicAuthentication('', personal_access_token)
        self.connection = Connection(base_url=organization_url, creds=self.credentials)
        self.project = project
        
        # Initialize clients for different services
        self.work_item_client = self.connection.clients.get_work_item_tracking_client()
        self.git_client = self.connection.clients.get_git_client()
        self.build_client = self.connection.clients.get_build_client()
        self.test_client = self.connection.clients.get_test_client()
        
        logger.info(f"Azure DevOps client initialized for {organization_url}")

    def get_work_item(self, work_item_id: int) -> WorkItem:
        """
        Get details of a work item by its ID.
        
        Args:
            work_item_id: The ID of the work item to retrieve.
            
        Returns:
            WorkItem object containing details of the specified work item.
        """
        logger.info(f"Fetching work item {work_item_id}")
        return self.work_item_client.get_work_item(
            work_item_id, 
            expand=WorkItemExpand.ALL
        )
    
    def extract_task_details(self, work_item: WorkItem) -> Dict[str, Any]:
        """
        Extract relevant details from a work item.
        
        Args:
            work_item: The WorkItem object to process.
            
        Returns:
            Dictionary containing parsed task details.
        """
        fields = work_item.fields
        
        # Extract common fields
        task_details = {
            'id': work_item.id,
            'title': fields.get('System.Title', ''),
            'description': fields.get('System.Description', ''),
            'acceptance_criteria': fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', ''),
            'state': fields.get('System.State', ''),
            'assigned_to': fields.get('System.AssignedTo', {}).get('displayName', '') if isinstance(fields.get('System.AssignedTo'), dict) else fields.get('System.AssignedTo', ''),
            'created_by': fields.get('System.CreatedBy', {}).get('displayName', '') if isinstance(fields.get('System.CreatedBy'), dict) else fields.get('System.CreatedBy', ''),
            'created_date': fields.get('System.CreatedDate', ''),
            'changed_date': fields.get('System.ChangedDate', ''),
            'work_item_type': fields.get('System.WorkItemType', ''),
            'tags': fields.get('System.Tags', '').split(';') if fields.get('System.Tags', '') else [],
            'priority': fields.get('Microsoft.VSTS.Common.Priority', 0),
        }
        
        # Extract repository information if available
        repo_info = self._extract_repository_info(fields)
        if repo_info:
            task_details['repository'] = repo_info
            
        logger.info(f"Extracted details for task {work_item.id}")
        return task_details
    
    def _extract_repository_info(self, fields: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Extract repository information from work item fields.
        
        This attempts to find repository information in various custom fields that
        might be used in different Azure DevOps setups.
        
        Args:
            fields: Work item fields dictionary.
            
        Returns:
            Dictionary with repository details or None if not found.
        """
        # Common field names that might contain repository information
        repo_field_candidates = [
            'Custom.Repository',
            'Custom.RepositoryUrl',
            'Microsoft.VSTS.Build.SourceRepository',
            'Custom.GitRepository',
        ]
        
        for field in repo_field_candidates:
            if field in fields and fields[field]:
                return {'url': fields[field]}
        
        # Try to extract from description or other fields if specific field not found
        description = fields.get('System.Description', '')
        if description and ('github.com/' in description or 'dev.azure.com/' in description):
            # Basic extraction logic - would need more robust implementation in production
            import re
            repo_urls = re.findall(r'(https?://[^\s]+?(?:github\.com|dev\.azure\.com)[^\s]+?(?:\.git|(?=/)))', description)
            if repo_urls:
                return {'url': repo_urls[0]}
                
        return None
    
    def create_pull_request(self, 
                          repository_id: str,
                          project: Optional[str] = None,
                          source_branch: str = '',
                          target_branch: str = 'main',
                          title: str = '',
                          description: str = '',
                          reviewers: Optional[List[str]] = None,
                          work_item_ids: Optional[List[int]] = None) -> GitPullRequest:
        """
        Create a pull request in Azure DevOps.
        
        Args:
            repository_id: ID or name of the repository
            project: Project name (uses default if not specified)
            source_branch: Source branch name
            target_branch: Target branch name (default: main)
            title: PR title
            description: PR description
            reviewers: List of reviewer IDs
            work_item_ids: List of related work item IDs
            
        Returns:
            GitPullRequest object representing the created PR
        """
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified either in constructor or method call")
            
        # Create PR object
        pull_request = GitPullRequest(
            source_ref_name=f"refs/heads/{source_branch}",
            target_ref_name=f"refs/heads/{target_branch}",
            title=title,
            description=description,
            work_item_refs=[{"id": str(id)} for id in (work_item_ids or [])]
        )
        
        logger.info(f"Creating PR from {source_branch} to {target_branch} in {repository_id}")
        created_pr = self.git_client.create_pull_request(pull_request, repository_id, project)
        
        # Add reviewers if specified
        if reviewers and created_pr.pull_request_id:
            for reviewer in reviewers:
                self.git_client.create_pull_request_reviewer(
                    {"id": reviewer},
                    repository_id,
                    created_pr.pull_request_id,
                    reviewer,
                    project
                )
        
        return created_pr
    
    def get_repositories(self, project: Optional[str] = None) -> List[GitRepository]:
        """
        Get all repositories in a project.
        
        Args:
            project: Project name (uses default if not specified)
            
        Returns:
            List of GitRepository objects
        """
        project = project or self.project
        if not project:
            raise ValueError("Project must be specified either in constructor or method call")
            
        return self.git_client.get_repositories(project)
    
    def add_comment_to_work_item(self, work_item_id: int, comment: str) -> None:
        """
        Add a comment to a work item.
        
        Args:
            work_item_id: ID of the work item
            comment: Comment text to add
        """
        logger.info(f"Adding comment to work item {work_item_id}")
        self.work_item_client.add_comment(comment, work_item_id)