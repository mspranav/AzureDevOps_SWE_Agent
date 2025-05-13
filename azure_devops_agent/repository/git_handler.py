"""
Git Handler module for Azure DevOps Integration Agent.

This module provides functionality to interact with Git repositories,
including cloning, creating branches, committing changes, and more.
"""

import os
import logging
import tempfile
import shutil
from typing import Optional, List, Dict, Any, Tuple
import git
from git import Repo

logger = logging.getLogger(__name__)

class GitHandler:
    """Class for handling Git repository operations."""
    
    def __init__(self, 
                 repository_url: str, 
                 local_path: Optional[str] = None,
                 branch: str = 'main',
                 credentials: Optional[Dict[str, str]] = None):
        """
        Initialize the Git handler.
        
        Args:
            repository_url: URL of the Git repository.
            local_path: Local path where the repository should be cloned (optional).
            branch: Default branch to work with (default: main).
            credentials: Git credentials if needed (username and password/token).
        """
        self.repository_url = repository_url
        self.branch = branch
        self.credentials = credentials
        
        # If local path is not provided, create a temporary directory
        if local_path:
            self.local_path = local_path
            self.temp_dir = None
        else:
            self.temp_dir = tempfile.mkdtemp(prefix='azdevops_')
            self.local_path = self.temp_dir
            
        self.repo = None
        logger.info(f"Git handler initialized for {repository_url}")
    
    def __del__(self):
        """Clean up temporary directory when the object is destroyed."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory {self.temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up temporary directory: {str(e)}")
    
    def _get_auth_url(self) -> str:
        """
        Get repository URL with embedded authentication if credentials are provided.
        
        Returns:
            Repository URL with authentication if credentials are available.
        """
        if not self.credentials:
            return self.repository_url
            
        # Parse URL to embed authentication
        if self.repository_url.startswith('https://'):
            username = self.credentials.get('username', '')
            password = self.credentials.get('password', '')
            
            # Format: https://username:password@github.com/...
            url_parts = self.repository_url.split('https://', 1)
            return f"https://{username}:{password}@{url_parts[1]}"
            
        return self.repository_url
    
    def clone_repository(self) -> str:
        """
        Clone the repository to the local path.
        
        Returns:
            Path to the cloned repository.
        """
        auth_url = self._get_auth_url()
        
        try:
            logger.info(f"Cloning repository to {self.local_path}")
            self.repo = Repo.clone_from(auth_url, self.local_path)
            return self.local_path
        except git.GitError as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            raise
    
    def open_repository(self) -> Repo:
        """
        Open an existing repository.
        
        Returns:
            Git Repo object.
        """
        if not os.path.exists(os.path.join(self.local_path, '.git')):
            raise ValueError(f"No Git repository found at {self.local_path}")
            
        try:
            logger.info(f"Opening repository at {self.local_path}")
            self.repo = Repo(self.local_path)
            return self.repo
        except git.GitError as e:
            logger.error(f"Failed to open repository: {str(e)}")
            raise
    
    def get_repository(self) -> Repo:
        """
        Get the current repository object, cloning or opening as needed.
        
        Returns:
            Git Repo object.
        """
        if self.repo is not None:
            return self.repo
            
        if os.path.exists(os.path.join(self.local_path, '.git')):
            return self.open_repository()
        else:
            return self.clone_repository()
    
    def create_branch(self, branch_name: str, base_branch: Optional[str] = None) -> None:
        """
        Create a new branch in the repository.
        
        Args:
            branch_name: Name of the branch to create.
            base_branch: Branch to base the new branch on (default: current HEAD).
        """
        repo = self.get_repository()
        
        # Checkout base branch if specified
        if base_branch:
            logger.info(f"Checking out base branch {base_branch}")
            repo.git.checkout(base_branch)
        
        # Create new branch
        logger.info(f"Creating new branch {branch_name}")
        repo.git.checkout('-b', branch_name)
    
    def add_files(self, file_paths: List[str]) -> None:
        """
        Add files to the staging area.
        
        Args:
            file_paths: List of file paths to add.
        """
        repo = self.get_repository()
        
        for file_path in file_paths:
            logger.info(f"Adding file to staging area: {file_path}")
            repo.git.add(file_path)
    
    def commit_changes(self, message: str, author: Optional[str] = None) -> str:
        """
        Commit staged changes.
        
        Args:
            message: Commit message.
            author: Author name and email in format "Name <email>".
            
        Returns:
            Commit hash.
        """
        repo = self.get_repository()
        
        commit_kwargs = {}
        if author:
            commit_kwargs['author'] = author
            
        logger.info(f"Committing changes with message: {message}")
        commit = repo.git.commit('-m', message, **commit_kwargs)
        
        # Extract commit hash
        return repo.git.rev_parse('HEAD')
    
    def push_changes(self, branch_name: Optional[str] = None, set_upstream: bool = True) -> None:
        """
        Push changes to the remote repository.
        
        Args:
            branch_name: Name of the branch to push (default: current branch).
            set_upstream: Whether to set the upstream branch (default: True).
        """
        repo = self.get_repository()
        
        # Use current branch if not specified
        if not branch_name:
            branch_name = repo.active_branch.name
            
        # Push with or without setting upstream
        if set_upstream:
            logger.info(f"Pushing branch {branch_name} with set-upstream")
            repo.git.push('--set-upstream', 'origin', branch_name)
        else:
            logger.info(f"Pushing branch {branch_name}")
            repo.git.push('origin', branch_name)
    
    def checkout_branch(self, branch_name: str) -> None:
        """
        Checkout an existing branch.
        
        Args:
            branch_name: Name of the branch to checkout.
        """
        repo = self.get_repository()
        
        logger.info(f"Checking out branch {branch_name}")
        repo.git.checkout(branch_name)
    
    def pull_latest_changes(self, branch_name: Optional[str] = None) -> None:
        """
        Pull latest changes from the remote repository.
        
        Args:
            branch_name: Name of the branch to pull (default: current branch).
        """
        repo = self.get_repository()
        
        # Checkout the branch if specified
        if branch_name:
            self.checkout_branch(branch_name)
            
        logger.info(f"Pulling latest changes for {repo.active_branch.name}")
        repo.git.pull()
    
    def get_file_content(self, file_path: str, revision: str = 'HEAD') -> str:
        """
        Get the content of a file from the repository.
        
        Args:
            file_path: Path to the file.
            revision: Git revision to read from (default: HEAD).
            
        Returns:
            Content of the file as a string.
        """
        repo = self.get_repository()
        
        try:
            logger.info(f"Reading file content: {file_path}")
            return repo.git.show(f"{revision}:{file_path}")
        except git.GitError as e:
            logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise
    
    def search_files(self, pattern: str) -> List[str]:
        """
        Search for files in the repository matching a pattern.
        
        Args:
            pattern: Glob pattern for files to search.
            
        Returns:
            List of matching file paths.
        """
        repo = self.get_repository()
        
        # Use git ls-files with glob pattern
        logger.info(f"Searching files with pattern: {pattern}")
        output = repo.git.ls_files(pattern)
        
        # Split output by lines and filter empty lines
        return [line for line in output.split('\n') if line.strip()]
    
    def get_repository_structure(self) -> Dict[str, Any]:
        """
        Get the structure of the repository.
        
        Returns:
            Dictionary representing the repository structure.
        """
        repo = self.get_repository()
        
        # Get all files in the repository
        all_files = repo.git.ls_files().split('\n')
        
        # Build directory structure
        structure = {}
        for file_path in all_files:
            if not file_path.strip():
                continue
                
            # Split path into components
            parts = file_path.split('/')
            current = structure
            
            # Build nested dictionary structure
            for i, part in enumerate(parts):
                # If this is the last part (file), store it
                if i == len(parts) - 1:
                    current.setdefault('files', []).append(part)
                # Otherwise, it's a directory
                else:
                    current.setdefault('directories', {}).setdefault(part, {})
                    current = current['directories'][part]
        
        logger.info(f"Retrieved repository structure with {len(all_files)} files")
        return structure