"""
Pull Request Manager module for Azure DevOps Integration Agent.

This module handles the creation and management of pull requests in Azure DevOps,
including formatting PR descriptions and handling reviewers.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from azure_devops_agent.core.azure_client import AzureDevOpsClient
from azure_devops_agent.repository.git_handler import GitHandler

logger = logging.getLogger(__name__)

class PRManager:
    """Manage pull requests in Azure DevOps."""
    
    def __init__(self, 
                 azure_client: AzureDevOpsClient,
                 git_handler: Optional[GitHandler] = None):
        """
        Initialize the PR manager.
        
        Args:
            azure_client: An initialized AzureDevOpsClient instance.
            git_handler: An optional GitHandler instance.
        """
        self.azure_client = azure_client
        self.git_handler = git_handler
        logger.info("PR manager initialized")
    
    def create_pull_request(self, 
                          task_id: str,
                          task_details: Dict[str, Any],
                          implementation_results: Dict[str, Any],
                          repository_id: str,
                          source_branch: str,
                          target_branch: str = 'main',
                          project: Optional[str] = None,
                          reviewers: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a pull request for a completed task.
        
        Args:
            task_id: ID of the task.
            task_details: Details of the task.
            implementation_results: Results of the implementation.
            repository_id: ID or name of the repository.
            source_branch: Source branch name.
            target_branch: Target branch name (default: main).
            project: Project name (default: from Azure client).
            reviewers: List of reviewer IDs.
            
        Returns:
            Dictionary with created PR details.
        """
        # Ensure branch changes are pushed
        if self.git_handler:
            logger.info(f"Ensuring changes are pushed to {source_branch}")
            try:
                self.git_handler.push_changes(source_branch, set_upstream=True)
            except Exception as e:
                logger.error(f"Failed to push changes: {str(e)}")
                return {
                    'status': 'error',
                    'message': f"Failed to push changes: {str(e)}"
                }
        
        # Create PR title
        title = self._create_pr_title(task_id, task_details)
        
        # Create PR description
        description = self._create_pr_description(
            task_id,
            task_details,
            implementation_results
        )
        
        try:
            # Create the PR in Azure DevOps
            logger.info(f"Creating PR for task {task_id} from {source_branch} to {target_branch}")
            pr = self.azure_client.create_pull_request(
                repository_id=repository_id,
                project=project,
                source_branch=source_branch,
                target_branch=target_branch,
                title=title,
                description=description,
                reviewers=reviewers,
                work_item_ids=[int(task_id)]
            )
            
            logger.info(f"PR created successfully: ID {pr.pull_request_id}")
            return {
                'status': 'success',
                'pr_id': pr.pull_request_id,
                'pr_url': pr.url,
                'title': title
            }
            
        except Exception as e:
            logger.error(f"Failed to create PR: {str(e)}")
            return {
                'status': 'error',
                'message': f"Failed to create PR: {str(e)}"
            }
    
    def _create_pr_title(self, task_id: str, task_details: Dict[str, Any]) -> str:
        """
        Create a PR title following the specified format.
        
        Args:
            task_id: ID of the task.
            task_details: Details of the task.
            
        Returns:
            Formatted PR title.
        """
        # Get task title or use a default
        task_title = task_details.get('title', 'Implement task')
        
        # Format according to spec: [Task #{task_number}] {Brief description} (AI Agent)
        title = f"[Task #{task_id}] {task_title} (AI Agent)"
        
        # Ensure title is not too long (Azure DevOps has a limit)
        max_length = 255
        if len(title) > max_length:
            title = title[:max_length-3] + "..."
            
        return title
    
    def _create_pr_description(self, 
                             task_id: str, 
                             task_details: Dict[str, Any],
                             implementation_results: Dict[str, Any]) -> str:
        """
        Create a PR description following the specified format.
        
        Args:
            task_id: ID of the task.
            task_details: Details of the task.
            implementation_results: Results of the implementation.
            
        Returns:
            Formatted PR description.
        """
        # Get implementation summary
        implementations = implementation_results.get('implementations', [])
        modified_files = [i['file'] for i in implementations if i['status'] == 'success']
        
        # Get test summary
        tests = implementation_results.get('tests', [])
        test_files = [t['file'] for t in tests if t['status'] in ['success', 'generated']]
        
        # Format description according to spec
        description = """
## Summary
{brief_description}

## Implemented Changes
{changes}

## Testing
{testing}

## Task Reference
This PR addresses Azure DevOps Task #{task_id}

_This pull request was created by an AI Agent_
"""
        
        # Extract brief description from task details
        brief_description = task_details.get('description', 'No description provided')
        if len(brief_description) > 500:
            brief_description = brief_description[:497] + "..."
            
        # Create changes list
        changes_list = []
        for implementation in implementations:
            file_path = implementation['file']
            action = implementation['action']
            language = implementation.get('language', '')
            
            changes_list.append(f"- **{action.capitalize()}** `{file_path}` ({language})")
            
        changes = "\n".join(changes_list) if changes_list else "- No changes implemented"
        
        # Create testing summary
        testing_list = []
        if test_files:
            testing_list.append(f"- Created/updated {len(test_files)} test files")
            for test_file in test_files:
                testing_list.append(f"  - `{test_file}`")
                
            # Add test results if available
            if any('tests_run' in t for t in tests):
                total_run = sum(t.get('tests_run', 0) for t in tests)
                total_passed = sum(t.get('tests_passed', 0) for t in tests)
                
                if total_run > 0:
                    testing_list.append(f"- Ran {total_run} tests, {total_passed} passed")
        else:
            testing_list.append("- No tests were created or run")
            
        testing = "\n".join(testing_list)
        
        # Format the final description
        formatted_description = description.format(
            brief_description=brief_description,
            changes=changes,
            testing=testing,
            task_id=task_id
        )
        
        return formatted_description
    
    def get_reviewers_for_repository(self, 
                                   repository_id: str, 
                                   project: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get potential reviewers for a repository.
        
        Args:
            repository_id: ID or name of the repository.
            project: Project name (default: from Azure client).
            
        Returns:
            List of potential reviewers.
        """
        # In a real implementation, this would use the Azure DevOps API to get
        # repository contributors or code owners
        # For now, this returns a placeholder
        logger.info(f"Getting reviewers for repository {repository_id}")
        
        # Return placeholder reviewers
        return [
            {'id': 'placeholder-id-1', 'displayName': 'Placeholder Reviewer 1'},
            {'id': 'placeholder-id-2', 'displayName': 'Placeholder Reviewer 2'}
        ]
    
    def format_pr_for_cross_repository_dependencies(self, 
                                                 description: str,
                                                 dependencies: List[Dict[str, Any]]) -> str:
        """
        Format PR description for cross-repository dependencies.
        
        Args:
            description: Original PR description.
            dependencies: List of repository dependencies.
            
        Returns:
            Updated PR description with dependency information.
        """
        if not dependencies:
            return description
            
        # Create dependencies section
        dependencies_section = "\n## Cross-Repository Dependencies\n"
        
        for dep in dependencies:
            repo_name = dep.get('name', 'Unknown repository')
            repo_url = dep.get('url', '#')
            dep_type = dep.get('type', 'dependency')
            
            dependencies_section += f"- **{repo_name}** ({dep_type})\n"
            dependencies_section += f"  - {repo_url}\n"
            
            if 'changes_needed' in dep and dep['changes_needed']:
                dependencies_section += "  - Changes required:\n"
                for change in dep['changes_needed']:
                    dependencies_section += f"    - {change}\n"
                    
        # Add to the original description
        updated_description = description + "\n" + dependencies_section
        
        return updated_description
    
    def format_pr_for_performance_optimization(self, 
                                            description: str,
                                            before_metrics: Dict[str, Any],
                                            after_metrics: Dict[str, Any]) -> str:
        """
        Format PR description for performance optimization tasks.
        
        Args:
            description: Original PR description.
            before_metrics: Performance metrics before changes.
            after_metrics: Performance metrics after changes.
            
        Returns:
            Updated PR description with performance comparison.
        """
        if not before_metrics or not after_metrics:
            return description
            
        # Create performance section
        perf_section = "\n## Performance Comparison\n"
        perf_section += "| Metric | Before | After | Change |\n"
        perf_section += "|--------|--------|-------|--------|\n"
        
        for metric in set(list(before_metrics.keys()) + list(after_metrics.keys())):
            before_value = before_metrics.get(metric, 'N/A')
            after_value = after_metrics.get(metric, 'N/A')
            
            # Calculate change if both values are numeric
            change = 'N/A'
            if isinstance(before_value, (int, float)) and isinstance(after_value, (int, float)):
                if before_value != 0:
                    percent_change = ((after_value - before_value) / before_value) * 100
                    change = f"{percent_change:.2f}%"
                else:
                    change = 'N/A (division by zero)'
                    
            perf_section += f"| {metric} | {before_value} | {after_value} | {change} |\n"
            
        # Add to the original description
        updated_description = description + "\n" + perf_section
        
        return updated_description
    
    def format_pr_for_feature_flag(self, 
                                 description: str,
                                 feature_flag: Dict[str, Any]) -> str:
        """
        Format PR description for feature flag implementation.
        
        Args:
            description: Original PR description.
            feature_flag: Feature flag information.
            
        Returns:
            Updated PR description with feature flag information.
        """
        if not feature_flag:
            return description
            
        # Create feature flag section
        flag_section = "\n## Feature Flag Information\n"
        
        flag_name = feature_flag.get('name', 'Unknown')
        flag_section += f"### Flag Name: `{flag_name}`\n\n"
        
        # Default state
        default_state = feature_flag.get('default_state', 'disabled')
        flag_section += f"Default state: **{default_state}**\n\n"
        
        # Configuration
        flag_section += "### Configuration\n"
        
        if 'configuration' in feature_flag:
            for env, config in feature_flag['configuration'].items():
                flag_section += f"#### {env} Environment\n"
                flag_section += f"- State: {config.get('state', 'not specified')}\n"
                
                if 'variables' in config:
                    flag_section += "- Variables:\n"
                    for key, value in config['variables'].items():
                        flag_section += f"  - `{key}`: `{value}`\n"
                        
        # Usage information
        flag_section += "\n### Usage Instructions\n"
        
        if 'usage' in feature_flag:
            flag_section += feature_flag['usage']
        else:
            flag_section += f"To enable the feature, set the `{flag_name}` flag to `true` in your configuration.\n"
            
        # Testing instructions
        flag_section += "\n### Testing\n"
        
        if 'testing' in feature_flag:
            flag_section += feature_flag['testing']
        else:
            flag_section += "- Test with the feature flag both enabled and disabled\n"
            flag_section += f"- To enable for testing, set `{flag_name}=true`\n"
            
        # Add to the original description
        updated_description = description + "\n" + flag_section
        
        return updated_description