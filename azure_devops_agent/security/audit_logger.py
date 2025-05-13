"""
Audit Logger module for Azure DevOps Integration Agent.

This module provides secure audit logging functionality to track all
agent actions for security and compliance purposes.
"""

import os
import logging
import json
import time
import uuid
import socket
import getpass
from typing import Dict, Optional, Any, List, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Audit logger for tracking security-relevant events.
    
    This class provides a structured way to log agent actions for security
    and compliance purposes, including task access, code changes, and
    authentication events.
    """
    
    # Event types for audit logging
    EVENT_AUTHENTICATION = "AUTHENTICATION"
    EVENT_TASK_ACCESS = "TASK_ACCESS"
    EVENT_REPOSITORY_ACCESS = "REPOSITORY_ACCESS"
    EVENT_CODE_CHANGE = "CODE_CHANGE"
    EVENT_PR_CREATION = "PR_CREATION"
    EVENT_CONFIGURATION = "CONFIGURATION"
    
    # Severity levels
    SEVERITY_INFO = "INFO"
    SEVERITY_WARN = "WARNING"
    SEVERITY_ERROR = "ERROR"
    
    def __init__(self, 
                 log_file: Optional[str] = None, 
                 log_to_console: bool = False,
                 log_to_azure: bool = False,
                 structured_format: bool = True):
        """
        Initialize the audit logger.
        
        Args:
            log_file: Path to the audit log file (optional).
            log_to_console: Whether to also log to console (default: False).
            log_to_azure: Whether to log to Azure Monitor (default: False).
            structured_format: Whether to use structured JSON logs (default: True).
        """
        self.log_file = log_file
        self.log_to_console = log_to_console
        self.log_to_azure = log_to_azure
        self.structured_format = structured_format
        
        # Set up file logger if log_file is specified
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Set up file handler
            file_handler = logging.FileHandler(log_file)
            
            if structured_format:
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
                
            file_handler.setFormatter(formatter)
            
            # Create a separate logger for audit events
            self.audit_logger = logging.getLogger("audit")
            self.audit_logger.setLevel(logging.INFO)
            self.audit_logger.addHandler(file_handler)
            
            # Ensure audit logger doesn't propagate to root logger
            self.audit_logger.propagate = False
            
            if log_to_console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.audit_logger.addHandler(console_handler)
                
        logger.info(f"Audit logger initialized with file: {log_file}")
    
    def log_event(self, 
                 event_type: str, 
                 severity: str, 
                 message: str,
                 user: Optional[str] = None,
                 task_id: Optional[str] = None,
                 repository: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an audit event.
        
        Args:
            event_type: Type of the event (use EVENT_* constants).
            severity: Severity level (use SEVERITY_* constants).
            message: Event message.
            user: Username associated with the event (optional).
            task_id: ID of the task associated with the event (optional).
            repository: Repository associated with the event (optional).
            details: Additional event details (optional).
            
        Returns:
            ID of the logged event.
        """
        # Generate event ID
        event_id = str(uuid.uuid4())
        
        # Get current time
        timestamp = datetime.utcnow().isoformat() + 'Z'  # ISO format with Z suffix for UTC
        
        # Get user if not provided
        if not user:
            user = getpass.getuser()
            
        # Get hostname
        hostname = socket.gethostname()
        
        # Create audit event
        audit_event = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "severity": severity,
            "message": message,
            "user": user,
            "host": hostname,
            "task_id": task_id,
            "repository": repository
        }
        
        # Add details if provided
        if details:
            audit_event["details"] = details
            
        # Log the event
        if self.log_file:
            if self.structured_format:
                self.audit_logger.info(json.dumps(audit_event))
            else:
                # Format as a readable message
                detail_str = f" - Details: {json.dumps(details)}" if details else ""
                task_str = f" - Task: {task_id}" if task_id else ""
                repo_str = f" - Repository: {repository}" if repository else ""
                
                self.audit_logger.info(
                    f"[{event_type}] {message} - User: {user}{task_str}{repo_str}{detail_str}"
                )
        else:
            # If no log file is specified, log to the main logger
            if self.structured_format:
                logger.info(f"AUDIT: {json.dumps(audit_event)}")
            else:
                detail_str = f" - Details: {json.dumps(details)}" if details else ""
                task_str = f" - Task: {task_id}" if task_id else ""
                repo_str = f" - Repository: {repository}" if repository else ""
                
                logger.info(
                    f"AUDIT: [{event_type}] {message} - User: {user}{task_str}{repo_str}{detail_str}"
                )
                
        # Log to Azure Monitor if enabled
        if self.log_to_azure:
            self._log_to_azure(audit_event)
            
        return event_id
    
    def log_authentication(self, 
                         user: str, 
                         success: bool, 
                         service: str,
                         details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an authentication event.
        
        Args:
            user: Username.
            success: Whether authentication was successful.
            service: Service being authenticated to.
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        severity = self.SEVERITY_INFO if success else self.SEVERITY_ERROR
        message = f"Authentication {'successful' if success else 'failed'} for service: {service}"
        
        event_details = {"service": service, "success": success}
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_AUTHENTICATION,
            severity=severity,
            message=message,
            user=user,
            details=event_details
        )
    
    def log_task_access(self, 
                      task_id: str, 
                      user: str,
                      action: str,
                      details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a task access event.
        
        Args:
            task_id: ID of the task.
            user: Username.
            action: Action performed on the task.
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        message = f"Task {action}: {task_id}"
        
        event_details = {"action": action}
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_TASK_ACCESS,
            severity=self.SEVERITY_INFO,
            message=message,
            user=user,
            task_id=task_id,
            details=event_details
        )
    
    def log_repository_access(self, 
                           repository: str,
                           user: str,
                           action: str,
                           branch: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a repository access event.
        
        Args:
            repository: Repository name or URL.
            user: Username.
            action: Action performed on the repository.
            branch: Branch name (optional).
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        message = f"Repository {action}: {repository}"
        if branch:
            message += f" (branch: {branch})"
            
        event_details = {"action": action}
        if branch:
            event_details["branch"] = branch
            
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_REPOSITORY_ACCESS,
            severity=self.SEVERITY_INFO,
            message=message,
            user=user,
            repository=repository,
            details=event_details
        )
    
    def log_code_change(self, 
                      repository: str,
                      user: str,
                      files_changed: List[str],
                      commit_id: Optional[str] = None,
                      branch: Optional[str] = None,
                      task_id: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a code change event.
        
        Args:
            repository: Repository name or URL.
            user: Username.
            files_changed: List of files that were changed.
            commit_id: Commit ID (optional).
            branch: Branch name (optional).
            task_id: Task ID (optional).
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        file_count = len(files_changed)
        message = f"Code change: {file_count} files changed in {repository}"
        if branch:
            message += f" (branch: {branch})"
            
        event_details = {
            "files_changed": files_changed,
            "file_count": file_count
        }
        
        if commit_id:
            event_details["commit_id"] = commit_id
            
        if branch:
            event_details["branch"] = branch
            
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_CODE_CHANGE,
            severity=self.SEVERITY_INFO,
            message=message,
            user=user,
            repository=repository,
            task_id=task_id,
            details=event_details
        )
    
    def log_pr_creation(self, 
                      repository: str,
                      user: str,
                      pr_id: str,
                      source_branch: str,
                      target_branch: str,
                      task_id: Optional[str] = None,
                      details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a pull request creation event.
        
        Args:
            repository: Repository name or URL.
            user: Username.
            pr_id: Pull request ID.
            source_branch: Source branch name.
            target_branch: Target branch name.
            task_id: Task ID (optional).
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        message = f"Pull request created: {pr_id} in {repository}"
        
        event_details = {
            "pr_id": pr_id,
            "source_branch": source_branch,
            "target_branch": target_branch
        }
        
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_PR_CREATION,
            severity=self.SEVERITY_INFO,
            message=message,
            user=user,
            repository=repository,
            task_id=task_id,
            details=event_details
        )
    
    def log_configuration_change(self, 
                              user: str,
                              config_name: str,
                              details: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a configuration change event.
        
        Args:
            user: Username.
            config_name: Name of the configuration.
            details: Additional details (optional).
            
        Returns:
            ID of the logged event.
        """
        message = f"Configuration changed: {config_name}"
        
        event_details = {"config_name": config_name}
        if details:
            event_details.update(details)
            
        return self.log_event(
            event_type=self.EVENT_CONFIGURATION,
            severity=self.SEVERITY_INFO,
            message=message,
            user=user,
            details=event_details
        )
    
    def _log_to_azure(self, audit_event: Dict[str, Any]) -> None:
        """
        Log an event to Azure Monitor.
        
        Args:
            audit_event: Audit event dictionary.
        """
        # This is a placeholder for the Azure Monitor logging implementation
        # In a real implementation, this would use Azure Monitor SDK or REST API
        logger.info(f"Would log to Azure Monitor: {json.dumps(audit_event)}")
        
        # Note: For a real implementation, you would use something like:
        # from azure.monitor.opentelemetry import AzureMonitorTraceExporter
        # exporter = AzureMonitorTraceExporter(connection_string="...")
        # exporter.export([audit_event])